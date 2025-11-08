"""
Utility functions for the complaint agent
"""

from typing import Tuple
from langchain_core.messages import HumanMessage
from .complaint_agent import agent, AgentState


def process_user_message(user_input: str, current_state: dict = None) -> Tuple[str, dict]:
    """
    Process a user message through the agent and return the response and updated state.
    
    Args:
        user_input: The user's message
        current_state: Current agent state (optional)
    
    Returns:
        Tuple of (response_text, updated_state)
    """
    from langchain_core.messages import AIMessage
    
    # Initialize state if not provided
    if current_state is None or current_state.get("messages") is None:
        state = {
            "messages": [],
            "complaint": None,
            "mobile_number": None,
            "summary": None,
            "confirmation": None,
            "submitted": False
        }
    else:
        # Deep copy the state, preserving messages
        state = {
            "messages": list(current_state.get("messages", [])),  # Copy message list
            "complaint": current_state.get("complaint"),
            "mobile_number": current_state.get("mobile_number"),
            "summary": current_state.get("summary"),
            "confirmation": current_state.get("confirmation"),
            "submitted": current_state.get("submitted", False)
        }
    
    # Add user message to state
    user_message = HumanMessage(content=user_input)
    state["messages"] = state.get("messages", []) + [user_message]
    
    # Invoke the agent
    config = {"recursion_limit": 20}
    try:
        result = agent.invoke(state, config)
    except Exception as e:
        # If agent fails, return a helpful error message
        error_response = f"I encountered an error processing your message. Please try again. Error: {str(e)}"
        return error_response, state
    
    # Get the last assistant message
    response_text = "I'm here to help you submit your complaint."
    messages = result.get("messages", [])
    for msg in reversed(messages):
        if isinstance(msg, AIMessage) and msg.content:
            response_text = msg.content
            break
    
    # Return response and updated state (but don't store all messages to avoid memory issues)
    return response_text, {
        "complaint": result.get("complaint"),
        "mobile_number": result.get("mobile_number"),
        "summary": result.get("summary"),
        "confirmation": result.get("confirmation"),
        "submitted": result.get("submitted", False),
        "messages": messages[-10:] if len(messages) > 10 else messages  # Keep only last 10 messages
    }

