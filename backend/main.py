"""
FastAPI Backend for Camila Call Taker
Wraps the LangGraph agent and provides REST API endpoints
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any
import sys
import os

# Add parent directory to path to import agent
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.agent.utils import process_user_message

app = FastAPI(title="Camila Call Taker API", version="1.0.0")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],  # React dev servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory session storage (in production, use Redis or database)
sessions: Dict[str, Dict[str, Any]] = {}


class ChatMessage(BaseModel):
    session_id: str
    message: str


class ChatResponse(BaseModel):
    response: str
    agent_state: Dict[str, Any]
    session_id: str


class SessionState(BaseModel):
    session_id: str
    state: Dict[str, Any]


@app.get("/")
async def root():
    """Health check endpoint"""
    return {"status": "healthy", "service": "Camila Call Taker API"}


@app.post("/api/chat", response_model=ChatResponse)
async def chat(chat_message: ChatMessage):
    """
    Process a chat message and return the agent's response
    """
    try:
        session_id = chat_message.session_id
        user_message = chat_message.message
        
        # Get or create session state
        if session_id not in sessions:
            sessions[session_id] = {
                "complaint": None,
                "mobile_number": None,
                "is_registered": None,
                "customer_data": {
                    "priorityId": None,
                    "sectorId": None,
                    "networkId": None,
                    "areaId": None,
                    "labId": None,
                    "commercialBranchCode": None,
                    "clientAddress": None
                },
                "address_loaded_from_system": None,
                "address_updated_by_user": None,
                "confirmation": None,
                "submitted": False,
                "messages": []
            }
        
        current_state = sessions[session_id]
        
        # Process message through agent
        response_text, updated_state = process_user_message(user_message, current_state)
        
        # Update session
        sessions[session_id] = updated_state
        
        return ChatResponse(
            response=response_text,
            agent_state=updated_state,
            session_id=session_id
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/session/clear")
async def clear_session(session_id: str):
    """Clear a session"""
    if session_id in sessions:
        del sessions[session_id]
    return {"status": "success", "message": "Session cleared"}


@app.get("/api/session/{session_id}")
async def get_session(session_id: str):
    """Get session state"""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    return {"session_id": session_id, "state": sessions[session_id]}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)

