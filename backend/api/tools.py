from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from backend.database.database import get_db
from backend.database.models import ToolAuditLog
# Import tools to ensure registration
import backend.tools.browser
import backend.tools.computer
import backend.tools.files
import backend.tools.screenshot
import backend.tools.system
from backend.tools.registry import tool_registry

router = APIRouter(prefix="/api/tools", tags=["Tools"])

class ToolExecuteRequest(BaseModel):
    tool_name: str
    arguments: Optional[Dict[str, Any]] = {}
    bypass_security: Optional[bool] = False

@router.get("")
def list_available_tools():
    """Returns list of registered JARVIS tools and schemas."""
    return tool_registry.list_tools()

@router.post("/execute")
def execute_tool(request: ToolExecuteRequest, db: Session = Depends(get_db)):
    """Executes a tool by name with parameter validation and audit logging."""
    res = tool_registry.execute(
        name=request.tool_name,
        args=request.arguments,
        bypass_security=request.bypass_security
    )

    # Log execution in database
    audit_entry = ToolAuditLog(
        tool_name=request.tool_name,
        arguments=request.arguments,
        result=str(res.get("result") or res.get("error") or res.get("message")),
        status=res.get("status", "UNKNOWN")
    )
    db.add(audit_entry)
    db.commit()

    return res

@router.get("/audit")
def get_tool_audit_logs(limit: int = 25, db: Session = Depends(get_db)):
    """Retrieve recent tool execution audit logs from SQLite."""
    logs = (
        db.query(ToolAuditLog)
        .order_by(ToolAuditLog.timestamp.desc())
        .limit(limit)
        .all()
    )
    return [
        {
            "id": str(log.id),
            "tool_name": log.tool_name,
            "status": log.status,
            "timestamp": log.timestamp.strftime("%H:%M:%S") if log.timestamp else "",
            "details": log.result[:120] if log.result else "",
            "arguments": log.arguments
        }
        for log in logs
    ]

