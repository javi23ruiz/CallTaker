import streamlit as st
from src.agent.utils import process_user_message

# Page configuration
st.set_page_config(
    page_title="CallTaker - Customer Complaints Agent",
    page_icon="📞",
    layout="wide"
)

# Initialize chat history and agent state
if "messages" not in st.session_state:
    st.session_state.messages = []

if "agent_state" not in st.session_state:
    st.session_state.agent_state = {
        "complaint": None,
        "mobile_number": None,
        "confirmation": None,
        "submitted": False
    }

# Custom CSS for better UI
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .chat-container {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1rem;
    }
    </style>
""", unsafe_allow_html=True)

# Header
st.markdown('<div class="main-header">📞 CallTaker - Customer Complaints Agent</div>', unsafe_allow_html=True)

# Sidebar for agent state
with st.sidebar:
    st.header("Agent State")
    
    # Always display state dict if it exists
    if st.session_state.agent_state is not None:
        # Display state dict without emojis
        state_dict = {
            "complaint": st.session_state.agent_state.get("complaint"),
            "mobile_number": st.session_state.agent_state.get("mobile_number"),
            "confirmation": st.session_state.agent_state.get("confirmation"),
            "submitted": st.session_state.agent_state.get("submitted", False)
        }
        st.json(state_dict)
    else:
        st.info("Start a conversation to see agent state")

# Main chat interface
st.subheader("Chat with the Agent")

# Display chat messages
chat_container = st.container()
with chat_container:
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Type your complaint or question here..."):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Process through agent
    with st.chat_message("assistant"):
        with st.spinner("Processing..."):
            try:
                response, updated_state = process_user_message(
                    prompt, 
                    st.session_state.agent_state
                )
                st.session_state.agent_state = updated_state
                st.markdown(response)
                st.session_state.messages.append({"role": "assistant", "content": response})
            except Exception as e:
                error_msg = f"Error: {str(e)}. Please check your .env file has OPENAI_API_KEY set."
                st.error(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})

# Clear chat button
if st.button("Clear Chat"):
    st.session_state.messages = []
    st.session_state.agent_state = {
        "complaint": None,
        "mobile_number": None,
        "confirmation": None,
        "submitted": False
    }
    st.rerun()

