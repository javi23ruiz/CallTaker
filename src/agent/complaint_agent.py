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

# Initialize OpenAI model
llm = ChatOpenAI(
    model="gpt-4o",
    temperature=0.7,
    api_key=os.getenv("OPENAI_API_KEY")
)


class AgentState(TypedDict):
    """State for the complaint agent"""
    messages: Annotated[list, add_messages]
    complaint: Optional[str]
    mobile_number: Optional[str]
    summary: Optional[str]
    confirmation: Optional[bool]
    submitted: bool


def process_conversation(state: AgentState) -> AgentState:
    """Process conversation and extract information"""
    messages = state["messages"]
    complaint = state.get("complaint")
    mobile_number = state.get("mobile_number")
    summary = state.get("summary")
    confirmation = state.get("confirmation")
    
    # Get the last user message
    last_user_message = None
    for msg in reversed(messages):
        if isinstance(msg, HumanMessage):
            last_user_message = msg.content
            break
    
    updates = {}
    
    # Extract complaint if not already collected
    if not complaint and last_user_message:
        extract_prompt = f"""Extract the customer complaint from this message. Return ONLY the complaint text, or "None" if no complaint is present.

Message: {last_user_message}
Complaint:"""
        response = llm.invoke(extract_prompt)
        extracted = response.content.strip()
        if extracted.lower() != "none" and len(extracted) > 10:
            updates["complaint"] = extracted
    
    # Extract mobile number if not already collected
    if not mobile_number and last_user_message:
        extract_prompt = f"""Extract the phone/mobile number from this message. Return ONLY digits (no spaces/dashes), or "None" if no number is present.

Message: {last_user_message}
Phone number:"""
        response = llm.invoke(extract_prompt)
        extracted = response.content.strip()
        # Clean digits only
        digits = ''.join(filter(str.isdigit, extracted))
        if digits and len(digits) >= 10:
            updates["mobile_number"] = digits
    
    # Generate summary if both collected but no summary yet
    current_complaint = updates.get("complaint") or complaint
    current_mobile = updates.get("mobile_number") or mobile_number
    if not summary and current_complaint and current_mobile:
        summary_prompt = f"""Create a concise summary of this customer complaint:

Complaint: {current_complaint}
Mobile Number: {current_mobile}

Summary:"""
        response = llm.invoke(summary_prompt)
        updates["summary"] = response.content.strip()
    
    # Check for confirmation
    if summary and confirmation is None and last_user_message:
        msg_lower = last_user_message.lower()
        if any(word in msg_lower for word in ["yes", "confirm", "correct", "right", "submit"]):
            updates["confirmation"] = True
        elif any(word in msg_lower for word in ["no", "not", "wrong", "incorrect", "cancel"]):
            updates["confirmation"] = False
    
    # Update state
    current_state = {**state, **updates}
    current_complaint = current_state.get("complaint")
    current_mobile = current_state.get("mobile_number")
    current_summary = current_state.get("summary")
    current_confirmation = current_state.get("confirmation")
    
    # Generate response
    system_prompt = """You are a helpful customer service agent collecting complaint information. Be friendly and conversational."""
    
    if not current_complaint:
        instruction = "Ask the customer to describe their complaint."
    elif not current_mobile:
        instruction = f"Complaint received. Ask the customer for their mobile/phone number."
    elif not current_summary:
        instruction = "You have both the complaint and mobile number. Generate a summary and present it to the customer for confirmation."
    elif current_confirmation is None:
        instruction = f"Present this summary to the customer and ask them to confirm if it's correct:\n\n{current_summary}"
    elif current_confirmation is False:
        instruction = "The customer declined. Ask if they want to start over or modify the information."
    elif current_confirmation is True and not current_state.get("submitted", False):
        instruction = "The customer confirmed. Thank them and inform them that the complaint will be submitted."
    else:
        instruction = "Thank the customer for their patience."
    
    # Build conversation history for context
    conversation_history = []
    for msg in messages[-5:]:  # Last 5 messages for context
        if isinstance(msg, HumanMessage):
            conversation_history.append(f"User: {msg.content}")
        elif isinstance(msg, AIMessage):
            conversation_history.append(f"Assistant: {msg.content}")
    
    prompt = f"""{system_prompt}

{instruction}

Recent conversation:
{chr(10).join(conversation_history) if conversation_history else 'None'}

Generate a natural, friendly response:"""
    
    try:
        response = llm.invoke(prompt)
        response_text = response.content.strip()
        if not response_text:
            response_text = "I'm here to help you submit your complaint. How can I assist you today?"
    except Exception as e:
        # Fallback response if LLM fails
        response_text = "I'm here to help you submit your complaint. Could you please describe your issue?"
        print(f"Error generating response: {e}")
    
    # Add assistant response to messages
    new_messages = messages + [AIMessage(content=response_text)]
    
    return {
        **current_state,
        "messages": new_messages
    }


def should_continue(state: AgentState) -> Literal["collect_info", "summarize", "get_confirmation", "submit", "end"]:
    """Determine next step based on current state"""
    complaint = state.get("complaint")
    mobile_number = state.get("mobile_number")
    summary = state.get("summary")
    confirmation = state.get("confirmation")
    submitted = state.get("submitted", False)
    
    if submitted:
        return "end"
    
    if not complaint or not mobile_number:
        return "collect_info"
    
    if not summary:
        return "summarize"
    
    if confirmation is None:
        return "get_confirmation"
    
    if confirmation is True:
        return "submit"
    
    return "end"


def submit_complaint(state: AgentState) -> AgentState:
    """Submit the complaint (placeholder for now)"""
    complaint = state.get("complaint")
    mobile_number = state.get("mobile_number")
    summary = state.get("summary")
    
    # TODO: Implement actual submission logic
    print(f"Complaint submitted:")
    print(f"Mobile: {mobile_number}")
    print(f"Summary: {summary}")
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
            "summarize": END,      # End after processing, wait for next user input
            "get_confirmation": END, # End after processing, wait for next user input
            "submit": "submit",    # Only submit if confirmed
            "end": END
        }
    )
    
    workflow.add_edge("submit", END)
    
    return workflow.compile()


# Create the agent instance
agent = create_complaint_agent()

