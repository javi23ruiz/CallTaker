"""
LangGraph Agent for Customer Complaints
Captures complaint and mobile number, summarizes, and submits on confirmation.
"""

import os
from typing import TypedDict, Annotated, Literal, Optional
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages

# Load environment variables
load_dotenv()

# Initialize OpenAI models
llm = ChatOpenAI(
    model="gpt-4o",
    temperature=0.7,
    api_key=os.getenv("OPENAI_API_KEY")
)

# Mini model for simple follow-up questions
llm_mini = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0.7,
    api_key=os.getenv("OPENAI_API_KEY")
)

# In-memory dictionary for registered users
REGISTERED_USERS = {
    "050555555": {
        "priorityId": "****",
        "sectorId": "*****",
        "networkId": "****",
        "areaId": "*****",
        "labId": "*****",
        "commercialBranchCode": "****",
        "clientAddress": "حي المعذر الشمالي، RGMA3235، 3235 موسى بن نصير، 6950, Riyadh 12332, Arabia Saudí"
    }
}


class AgentState(TypedDict):
    """State for the complaint agent"""
    messages: Annotated[list, add_messages]
    complaint: Optional[str]
    mobile_number: Optional[str]
    is_registered: Optional[bool]
    customer_data: Optional[dict]
    address_loaded_from_system: Optional[bool]
    address_updated_by_user: Optional[bool]
    confirmation: Optional[bool]
    submitted: bool


def process_conversation(state: AgentState) -> AgentState:
    """Process conversation and extract information"""
    messages = state["messages"]
    complaint = state.get("complaint")
    mobile_number = state.get("mobile_number")
    is_registered = state.get("is_registered")
    customer_data = state.get("customer_data", {})
    confirmation = state.get("confirmation")
    
    # Get the last user message
    last_user_message = None
    for msg in reversed(messages):
        if isinstance(msg, HumanMessage):
            last_user_message = msg.content
            break
    
    updates = {}
    
    # Extract complaint from current message if not already collected
    if not complaint and last_user_message:
        extract_prompt = f"""Extract the customer complaint from this message. Return ONLY the complaint text, or "None" if no complaint is present.

Message: {last_user_message}
Complaint:"""
        response = llm.invoke(extract_prompt)
        extracted = response.content.strip()
        if extracted.lower() != "none" and len(extracted) > 10:
            updates["complaint"] = extracted
    
    # Extract mobile number from current message if not already collected
    if not mobile_number and last_user_message:
        # First, try to extract any sequence of digits from the message
        digits_in_message = ''.join(filter(str.isdigit, last_user_message))
        
        # If we found digits and it looks like a phone number (5+ digits), use it
        # Otherwise, ask the LLM to determine if there's a phone number
        if digits_in_message and len(digits_in_message) >= 5:
            # We found a reasonable number of digits, likely a phone number
            updates["mobile_number"] = digits_in_message
            # Check registration immediately after extraction
            is_registered = digits_in_message in REGISTERED_USERS
            updates["is_registered"] = is_registered
            # Populate customer_data if registered
            if is_registered:
                updates["customer_data"] = REGISTERED_USERS[digits_in_message].copy()
                updates["address_loaded_from_system"] = True  # Mark as loaded, not updated by user
            else:
                updates["customer_data"] = {
                    "priorityId": None,
                    "sectorId": None,
                    "networkId": None,
                    "areaId": None,
                    "labId": None,
                    "commercialBranchCode": None,
                    "clientAddress": None
                }
                updates["address_loaded_from_system"] = False
        else:
            # Let LLM decide if a phone number was provided (in case it's in text format)
            extract_prompt = f"""Analyze this message and determine if the user provided a phone/mobile number in words (e.g., "call me at...", "my number is..."). 
If a phone number is mentioned in text, extract it and return ONLY the digits (no spaces, dashes, or words).
If no phone number is present, return exactly "None".

Message: {last_user_message}
Phone number (digits only, or "None"):"""
            response = llm.invoke(extract_prompt)
            extracted = response.content.strip()
            
            # Check if LLM found a phone number in text
            if extracted.lower() != "none" and extracted:
                # Clean to get only digits
                text_digits = ''.join(filter(str.isdigit, extracted))
                # If we have digits, use them
                if text_digits and len(text_digits) >= 5:
                    updates["mobile_number"] = text_digits
                    # Check registration immediately after extraction
                    is_registered = text_digits in REGISTERED_USERS
                    updates["is_registered"] = is_registered
                    # Populate customer_data if registered
                    if is_registered:
                        updates["customer_data"] = REGISTERED_USERS[text_digits].copy()
                        updates["address_loaded_from_system"] = True  # Mark as loaded, not updated by user
                    else:
                        updates["customer_data"] = {
                            "priorityId": None,
                            "sectorId": None,
                            "networkId": None,
                            "areaId": None,
                            "labId": None,
                            "commercialBranchCode": None,
                            "clientAddress": None
                        }
                        updates["address_loaded_from_system"] = False
    
    # Immediately update state with any extractions
    if updates:
        state = {**state, **updates}
        # Update local variables to reflect changes
        complaint = state.get("complaint")
        mobile_number = state.get("mobile_number")
        is_registered = state.get("is_registered")
        customer_data = state.get("customer_data", {})
    
    # Extract address for non-registered customers if not already collected
    # OR for registered customers who want to provide a new address
    should_extract_address = (
        mobile_number and 
        last_user_message and
        (
            (is_registered is False and customer_data.get("clientAddress") is None) or  # Non-registered, no address
            (is_registered is True and confirmation is None and 
             any(phrase in last_user_message.lower() for phrase in ["new address", "different address", "my address is", "the address is"]))  # Registered wants new address
        )
    )
    
    if should_extract_address:
        # Ask LLM to extract address from the message
        extract_prompt = f"""Analyze this message and determine if the user provided an address or location.
If an address/location is mentioned, extract it and return it.
If no address is present, return exactly "None".

Message: {last_user_message}
Address:"""
        response = llm.invoke(extract_prompt)
        extracted_address = response.content.strip()
        
        if extracted_address.lower() != "none" and len(extracted_address) > 5:
            # Update customer_data with the provided address
            updated_customer_data = customer_data.copy()
            updated_customer_data["clientAddress"] = extracted_address
            updates["customer_data"] = updated_customer_data
            updates["address_updated_by_user"] = True  # Mark that user provided the address
    
    # Apply address updates if any
    if updates:
        state = {**state, **updates}
        # Refresh local variables after applying updates
        complaint = state.get("complaint")
        mobile_number = state.get("mobile_number")
        is_registered = state.get("is_registered")
        customer_data = state.get("customer_data", {})
    
    # Check for confirmation if both complaint and mobile are collected AND address is collected (if needed)
    current_complaint = complaint  # Use updated complaint from state
    current_mobile = mobile_number  # Use updated mobile from state
    current_is_registered = state.get("is_registered")
    current_customer_data = state.get("customer_data", {})
    current_has_address = current_customer_data.get("clientAddress") is not None
    
    # Check if we're ready for confirmation (address collected if needed)
    ready_for_confirmation = (
        current_complaint and 
        current_mobile and 
        (current_is_registered or current_has_address)  # Registered OR has address
    )
    
    if ready_for_confirmation and confirmation is None and last_user_message:
        msg_lower = last_user_message.lower()
        
        # Check if user is providing/changing address (with "no" or "change")
        wants_new_address = any(phrase in msg_lower for phrase in ["new address", "different address", "another address", "change address", "change the address", "change it to"])
        
        # If user says "no" or "change" but also provides an address, extract it
        if (wants_new_address or "no" in msg_lower or "change" in msg_lower) and len(last_user_message) > 10:
            # Try to extract address from the message
            extract_prompt = f"""Analyze this message and determine if the user provided a new address or location.
If an address/location is mentioned, extract it and return it.
If no address is present, return exactly "None".

Message: {last_user_message}
Address:"""
            response = llm.invoke(extract_prompt)
            extracted_address = response.content.strip()
            
            if extracted_address.lower() != "none" and len(extracted_address) > 5:
                # User provided a new address - update it
                updated_customer_data = current_customer_data.copy()
                updated_customer_data["clientAddress"] = extracted_address
                updates["customer_data"] = updated_customer_data
                updates["address_updated_by_user"] = True  # Mark that user updated the address
                # Don't set confirmation yet - will show new confirmation with updated address
            elif any(phrase in msg_lower for phrase in ["new address", "different address", "another address"]):
                # User wants new address but hasn't provided it yet - don't confirm yet
                pass
            else:
                # User said no without providing address - decline
                updates["confirmation"] = False
        elif any(word in msg_lower for word in ["yes", "confirm", "correct", "right", "submit", "this address"]):
            updates["confirmation"] = True
    
    # Check if address was just updated BY USER in this iteration
    address_just_updated_by_user = updates.get("address_updated_by_user", False)
    
    # Apply all updates to state (including confirmation if set)
    if updates:
        state = {**state, **updates}
    
    # Get current values for response generation (AFTER applying updates)
    current_state = state
    current_complaint = current_state.get("complaint")
    current_mobile = current_state.get("mobile_number")
    current_confirmation = current_state.get("confirmation")
    current_is_registered = current_state.get("is_registered")
    current_customer_data = current_state.get("customer_data", {})
    current_has_address = current_customer_data.get("clientAddress") is not None
    
    # Determine which model to use and build prompt
    # Use mini for simple follow-ups, gpt-4o for complex tasks
    use_mini = False
    
    # Build conversation history for context
    conversation_history = []
    for msg in messages[-5:]:  # Last 5 messages for context
        if isinstance(msg, HumanMessage):
            conversation_history.append(f"User: {msg.content}")
        elif isinstance(msg, AIMessage):
            conversation_history.append(f"{msg.content}")
    
    system_prompt = """You are Camila, a customer service AI assistant. Your role is to help customers report technical issues and complaints.

Communication Style:
- Be warm, empathetic, and professional
- Show genuine concern for their issues
- Be proactive and reassuring ("Let's get this sorted right away")
- Explain what you're doing and what happens next
- Use natural, conversational language
- Keep responses concise but complete

Always:
- Express empathy for their situation
- Be transparent about the process
- Confirm details clearly before submission
- Explain next steps after submission"""
    
    if not current_complaint:
        instruction = """Greet the customer warmly. Introduce yourself as Camila, their customer service AI assistant. 
Explain that you're here to help them report any technical issues or complaints they're facing.
Then ask them to describe the issue they're experiencing.

Example tone: "Hi, good morning! I'm Camila, your customer service AI assistant. I'm here to help you report any technical issues you're facing today."

Be warm, professional, and welcoming."""
        use_mini = False  # Use gpt-4o for initial greeting/asking for complaint
    elif not current_mobile:
        instruction = f"""Complaint received: {current_complaint}

Respond with empathy and reassurance:
1. Express empathy for their issue (e.g., "Oh no, I'm really sorry you're dealing with that" or "That must be frustrating")
2. Be proactive: "Let's get this sorted right away"
3. Explain the process: "I'll raise a report to our technical team. I just need a couple of details first."
4. Ask for their phone number politely: "Can we start with your phone number, please?"

Be warm, empathetic, and reassuring. Keep it concise."""
        use_mini = False  # Use gpt-4o for empathetic response
    elif current_mobile and current_is_registered is False and not current_has_address:
        # Non-registered customer needs to provide address
        instruction = f"""Complaint: {current_complaint}
Mobile Number: {current_mobile}
Customer is NOT registered.

Response:
1. Acknowledge the phone number: "Thank you"
2. Ask for the address: "Can you please provide the address where the issue is happening?" or "Could you share the location where you're experiencing this issue?"

Be polite and clear."""
        use_mini = True
    elif address_just_updated_by_user and current_confirmation is None:
        # Address was just updated BY USER - acknowledge it and ask for confirmation
        new_address = current_customer_data.get("clientAddress", "")
        instruction = f"""Complaint: {current_complaint}
Mobile Number: {current_mobile}
NEW Address just provided by customer: {new_address}

Provide clear confirmation:
"Just to confirm—you're reporting [brief issue] at this address: {new_address}. Anything else you'd like to add before I submit the report?"

Show the full address clearly. Be professional and warm."""
        use_mini = False  # Use gpt-4o for personalized response
    elif current_confirmation is None and current_complaint and current_mobile and current_has_address:
        # Ready for confirmation
        if current_is_registered:
            # Registered customer - mention the address found
            address = current_customer_data.get("clientAddress", "")
            instruction = f"""Complaint: {current_complaint}
Mobile Number: {current_mobile}
Customer is REGISTERED.
Address found in system: {address}

Response structure:
1. Acknowledge receipt: "Thank you."
2. Show you're checking: "Let me check..." or "I see..."
3. Present the address: "yes, I see an address linked to this number. It shows as: {address}"
4. Ask for confirmation: "Should I file the complaint for this location?" or "Would you like me to submit this complaint with this address or would you prefer to use a different one?"

Keep it natural and professional. Show the FULL address clearly."""
            use_mini = False  # Use gpt-4o for more nuanced message
        else:
            # Non-registered customer - normal confirmation
            address = current_customer_data.get("clientAddress", "")
            instruction = f"""Complaint: {current_complaint}
Mobile Number: {current_mobile}
Address provided: {address}

Provide a clear confirmation:
"Just to confirm—you're reporting [brief issue description] at this address: {address}. Anything else you'd like to add before I submit the report?"

Be clear, professional, and show the full address."""
            use_mini = False
    elif current_mobile and current_complaint and current_confirmation is None and not current_has_address and last_user_message and any(phrase in last_user_message.lower() for phrase in ["new address", "different address", "another address"]):
        # User asked for new address but hasn't provided it yet - prompt them to provide it
        instruction = "The customer wants to provide a different address. Acknowledge and ask them politely: 'Of course, could you please provide the address where the issue is happening?' Be warm and professional."
        use_mini = True
    elif current_confirmation is False:
        instruction = "The customer declined. Be understanding and helpful: 'No problem! What would you like to change or update?' Be warm and accommodating."
        use_mini = True  # Simple follow-up
    elif current_confirmation is True and not current_state.get("submitted", False):
        instruction = """The customer confirmed the submission.

Response structure:
1. Thank them: "Great, thank you" or "Perfect, thank you"
2. Confirm submission: "Your issue has been reported successfully"
3. Explain next steps: "Our technical team will review it and should contact you soon for a visit" or "Our team will look into this and contact you shortly"
4. Offer continued help: "If you need anything else in the meantime, I'm here to help"

Be warm, reassuring, and clear about what happens next. Example from Alora: "Great, thank you. Your issue has been reported successfully. Our technical team will review it and should contact you soon for a visit. If you need anything else in the meantime, I'm here to help." """
        use_mini = False  # Use gpt-4o for complete closure message
        # Mark as submitted and reset for next complaint
        updates["submitted"] = True
        updates["complaint"] = None  # Reset complaint for next one
        updates["confirmation"] = None  # Reset confirmation for next one
        # Keep customer_data - do NOT reset it
        # Keep is_registered - do NOT reset it
        # Keep mobile_number as it's the same customer
        updates["address_loaded_from_system"] = None  # Reset flags for next complaint
        updates["address_updated_by_user"] = None  # Reset flags for next complaint
    elif current_state.get("submitted", False) and not current_complaint:
        # Post-submission: offer to help with new complaint or end conversation
        instruction = "The previous complaint was submitted. Ask warmly if they have another issue they'd like to report: 'Is there anything else I can help you with today?' or 'Do you have another issue you'd like to report?' Be helpful and available."
        use_mini = True
    else:
        instruction = "Continue the conversation naturally based on the context."
        use_mini = True
    
    # Apply any additional updates before generating response
    if updates:
        state = {**state, **updates}
    
    prompt = f"""{system_prompt}

{instruction}

Recent conversation:
{chr(10).join(conversation_history) if conversation_history else 'None'}

Generate a natural, friendly response:"""
    
    # Use appropriate model
    model_to_use = llm_mini if use_mini else llm
    
    try:
        response = model_to_use.invoke(prompt)
        response_text = response.content.strip()
        if not response_text:
            # If empty, try again with the other model
            response = llm.invoke(prompt)
            response_text = response.content.strip()
    except Exception as e:
        # Try with the other model if first fails
        try:
            model_to_use = llm if use_mini else llm_mini
            response = model_to_use.invoke(prompt)
            response_text = response.content.strip()
        except Exception as e2:
            # Last resort: use gpt-4o
            response = llm.invoke(prompt)
            response_text = response.content.strip()
        print(f"Error generating response: {e}")
    
    # Add assistant response to messages
    new_messages = state.get("messages", []) + [AIMessage(content=response_text)]
    
    # Return updated state with all changes (including the submitted flag and reset fields)
    return {
        **state,
        "messages": new_messages
    }


def should_continue(state: AgentState) -> Literal["collect_info", "get_confirmation", "submit", "end"]:
    """Determine next step based on current state"""
    complaint = state.get("complaint")
    mobile_number = state.get("mobile_number")
    confirmation = state.get("confirmation")
    submitted = state.get("submitted", False)
    
    if submitted:
        return "end"
    
    if not complaint or not mobile_number:
        return "collect_info"
    
    if confirmation is None:
        return "get_confirmation"
    
    if confirmation is True:
        return "submit"
    
    return "end"


def submit_complaint(state: AgentState) -> AgentState:
    """Submit the complaint (placeholder for now)"""
    complaint = state.get("complaint")
    mobile_number = state.get("mobile_number")
    
    # TODO: Implement actual submission logic
    print(f"Complaint submitted:")
    print(f"Mobile: {mobile_number}")
    print(f"Full Complaint: {complaint}")
    
    return {
        **state,
        "submitted": True
    }


# Build the graph
def create_complaint_agent():
    """Create and return the complaint agent graph"""
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("process", process_conversation)
    workflow.add_node("submit", submit_complaint)
    
    # Set entry point
    workflow.set_entry_point("process")
    
    # Add conditional edges - process once and end, unless we need to submit
    workflow.add_conditional_edges(
        "process",
        should_continue,
        {
            "collect_info": END,  # End after processing, wait for next user input
            "get_confirmation": END, # End after processing, wait for next user input
            "submit": "submit",    # Only submit if confirmed
            "end": END
        }
    )
    
    workflow.add_edge("submit", END)
    
    return workflow.compile()


# Create the agent instance
agent = create_complaint_agent()

