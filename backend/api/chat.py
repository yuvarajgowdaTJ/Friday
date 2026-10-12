import logging
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from backend.database.database import get_db
from backend.database.models import ConversationMessage, ToolAuditLog
from backend.core.agent_router import NaturalLanguageAgent

logger = logging.getLogger("JARVIS.API.Chat")

router = APIRouter(prefix="/api/chat", tags=["Chat"])

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = "default"

class ChatResponse(BaseModel):
    response: str
    mode: str
    session_id: str
    tool_calls: Optional[List[Dict[str, Any]]] = None

@router.post("", response_model=ChatResponse)
def chat_endpoint(request: ChatRequest, db: Session = Depends(get_db)):
    """Primary chat endpoint connecting natural language input to the central AI Agent."""
    raw_text = request.message.strip()
    if not raw_text:
        raise HTTPException(status_code=400, detail="Message cannot be empty.")

    # 1. Save User message to SQLite DB
    user_msg_db = ConversationMessage(
        session_id=request.session_id,
        role="user",
        content=raw_text
    )
    db.add(user_msg_db)
    db.commit()

    # 2. Process message through Central Natural-Language Agent Router
    agent_result = NaturalLanguageAgent.process_request(
        user_message=raw_text,
        session_id=request.session_id,
        db=db
    )

    assistant_response = agent_result.get("response", "Request completed.")
    response_mode = agent_result.get("mode", "natural_agent")
    tool_calls = agent_result.get("tool_calls") or []

    # 3. Record all real tool executions in ToolAuditLog SQLite DB
    for tool_call in tool_calls:
        tool_name = tool_call.get("tool_name") or tool_call.get("name") or "unknown_tool"
        audit = ToolAuditLog(
            tool_name=tool_name,
            arguments=tool_call.get("arguments"),
            result=str(tool_call.get("result") or tool_call.get("error") or tool_call.get("message") or tool_call.get("summary")),
            status=tool_call.get("status", "SUCCESS")
        )
        db.add(audit)
    db.commit()

    # 4. Save Assistant response to SQLite DB
    assistant_msg_db = ConversationMessage(
        session_id=request.session_id,
        role="assistant",
        content=assistant_response,
        tool_calls=tool_calls if tool_calls else None
    )
    db.add(assistant_msg_db)
    db.commit()

    return ChatResponse(
        response=assistant_response,
        mode=response_mode,
        session_id=request.session_id,
        tool_calls=tool_calls if tool_calls else None
    )

@router.get("/history/{session_id}")
def get_chat_history(session_id: str = "default", limit: int = 50, db: Session = Depends(get_db)):
    """Retrieve chat history for a session."""
    messages = (
        db.query(ConversationMessage)
        .filter(ConversationMessage.session_id == session_id)
        .order_by(ConversationMessage.timestamp.asc())
        .limit(limit)
        .all()
    )
    return [
        {
            "id": m.id,
            "role": m.role,
            "content": m.content,
            "timestamp": m.timestamp.isoformat() if m.timestamp else None,
            "tool_calls": m.tool_calls
        }
        for m in messages
    ]
