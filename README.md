# CallTaker
Customer Complaints Agent using LangGraph and OpenAI

## Project Structure
```
CallTaker/
├── streamlit_app.py      # Main Streamlit application
├── requirements.txt      # Python dependencies
├── .env                  # Environment variables (create this file)
├── .gitignore           # Git ignore rules
├── src/
│   ├── __init__.py
│   └── agent/           # LangGraph agent implementation
│       ├── __init__.py
│       ├── complaint_agent.py  # Main agent logic
│       └── utils.py            # Helper functions
└── README.md
```

## Setup Instructions

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Create `.env` file:**
   Create a `.env` file in the root directory with the following content:
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   ```
   
   **Note:** The agent uses GPT-4o by default. Make sure your OpenAI API key has access to this model.

3. **Run the Streamlit app:**
   ```bash
   streamlit run streamlit_app.py
   ```

## Features

The agent follows this workflow:
1. **Collect Complaint**: Asks the customer to describe their complaint
2. **Collect Mobile Number**: Requests the customer's mobile/phone number
3. **Generate Summary**: Creates a summary of the complaint and mobile number
4. **Get Confirmation**: Presents the summary and asks for confirmation
5. **Submit**: Submits the complaint after user confirmation

## Current Status
- ✅ Streamlit chatbot interface
- ✅ LangGraph agent implementation
- ✅ Backend connection
- ✅ State management for conversation flow
- ⏳ Actual submission endpoint (currently prints to console)

## How It Works

The agent uses LangGraph to manage conversation state and flow:
- **State**: Tracks complaint, mobile number, summary, confirmation, and submission status
- **Nodes**: Process conversation, extract information, generate responses
- **Edges**: Conditional routing based on what information has been collected

The sidebar shows the current agent state, including what information has been collected.
