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


class AgentState(TypedDict):
    """State for the complaint agent"""
    messages: Annotated[list, add_messages]
    complaint: Optional[str]
    mobile_number: Optional[str]
    confirmation: Optional[bool]
    submitted: bool


def process_conversation(state: AgentState) -> AgentState:
    """Process conversation and extract information"""
    messages = state["messages"]
    complaint = state.get("complaint")
    mobile_number = state.get("mobile_number")
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
        # Let LLM decide if a phone number was provided
        extract_prompt = f"""Analyze this message and determine if the user provided a phone/mobile number. 
If a phone number is present, extract it and return ONLY the digits (no spaces, dashes, or words).
If no phone number is present, return exactly "None".

Message: {last_user_message}
Phone number (digits only, or "None"):"""
        response = llm.invoke(extract_prompt)
        extracted = response.content.strip()
        
        # Check if LLM found a phone number
        if extracted.lower() != "none" and extracted:
            # Clean to get only digits
            digits = ''.join(filter(str.isdigit, extracted))
            # If we have digits, use them (let LLM decide validity)
            if digits:
                updates["mobile_number"] = digits
    
    # Immediately update state with any extractions
    if updates:
        state = {**state, **updates}
        # Update local variables to reflect changes
        complaint = state.get("complaint")
        mobile_number = state.get("mobile_number")
    
    # Check for confirmation if both complaint and mobile are collected
    current_complaint = complaint  # Use updated complaint from state
    current_mobile = mobile_number  # Use updated mobile from state
    if current_complaint and current_mobile and confirmation is None and last_user_message:
        msg_lower = last_user_message.lower()
        if any(word in msg_lower for word in ["yes", "confirm", "correct", "right", "submit"]):
            updates["confirmation"] = True
        elif any(word in msg_lower for word in ["no", "not", "wrong", "incorrect", "cancel"]):
            updates["confirmation"] = False
    
    # Apply all updates to state (including confirmation if set)
    if updates:
        state = {**state, **updates}
    
    # Get current values for response generation
    current_state = state
    current_complaint = current_state.get("complaint")
    current_mobile = current_state.get("mobile_number")
    current_confirmation = current_state.get("confirmation")
    
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
    
    system_prompt = """You are a helpful customer service agent collecting complaint information. Be friendly and conversational."""
    
    if not current_complaint:
        instruction = "Ask the customer to describe their complaint."
        use_mini = False  # Use gpt-4o for initial greeting/asking for complaint
    elif not current_mobile:
        instruction = f"Complaint received: {current_complaint}\n\nAsk the customer for their mobile/phone number."
        use_mini = True  # Simple follow-up question
    elif current_confirmation is None:
        instruction = f"Complaint: {current_complaint}\nMobile Number: {current_mobile}\n\nPresent a friendly, short summary with bullet points (2-3 points max) of the complaint details, then ask for confirmation to submit it to the system. Be warm and friendly. Ask: 'Would you like me to submit this complaint to our system?'"
        use_mini = True  # Simple confirmation question
    elif current_confirmation is False:
        instruction = "The customer declined the summary. Ask if they want to start over or modify the information."
        use_mini = True  # Simple follow-up
    elif current_confirmation is True and not current_state.get("submitted", False):
        instruction = "The customer confirmed. Thank them and inform them that the complaint will be submitted."
        use_mini = True  # Simple acknowledgment
    else:
        instruction = "Continue the conversation naturally based on the context."
        use_mini = True
    
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
    
    # Return updated state with all changes
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

