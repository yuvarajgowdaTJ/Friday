import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, Boolean
from backend.database.database import Base

class ConversationMessage(Base):
    __tablename__ = "conversation_messages"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(50), index=True, default="default")
    role = Column(String(20), nullable=False) # user, assistant, system, tool
    content = Column(Text, nullable=False)
    tool_calls = Column(JSON, nullable=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

class MemoryItem(Base):
    __tablename__ = "memories"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(100), index=True)
    value = Column(Text, nullable=False)
    category = Column(String(50), default="general") # preference, fact, goal, user_info
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

class TaskPlanModel(Base):
    __tablename__ = "task_plans"

    id = Column(Integer, primary_key=True, index=True)
    plan_id = Column(String(50), index=True, unique=True)
    user_query = Column(Text, nullable=False)
    status = Column(String(20), default="PENDING") # PENDING, IN_PROGRESS, COMPLETED, FAILED
    steps = Column(JSON, nullable=False)
    result = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class ToolAuditLog(Base):
    __tablename__ = "tool_audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    tool_name = Column(String(100), index=True)
    arguments = Column(JSON, nullable=True)
    result = Column(Text, nullable=True)
    status = Column(String(20), default="SUCCESS") # SUCCESS, ERROR, CONFIRMATION_REQUIRED, REJECTED
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
