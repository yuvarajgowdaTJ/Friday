from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List
from sqlalchemy.orm import Session
from backend.database.database import get_db
from backend.core.memory import MemoryManager

router = APIRouter(prefix="/api/memory", tags=["Memory"])

class MemoryCreateRequest(BaseModel):
    key: str
    value: str
    category: Optional[str] = "general"

@router.get("")
def list_memories(db: Session = Depends(get_db)):
    """List all long-term memories."""
    return MemoryManager.get_all_memories(db=db)

@router.post("")
def create_memory(request: MemoryCreateRequest, db: Session = Depends(get_db)):
    """Store a memory or preference."""
    if not request.key.strip() or not request.value.strip():
        raise HTTPException(status_code=400, detail="Key and value cannot be empty.")
    return MemoryManager.add_memory(key=request.key, value=request.value, category=request.category, db=db)

@router.get("/search")
def search_memory(query: str, db: Session = Depends(get_db)):
    """Search stored memories."""
    return MemoryManager.search_memories(query=query, db=db)

@router.delete("/{memory_id}")
def delete_memory(memory_id: int, db: Session = Depends(get_db)):
    """Delete a memory item."""
    success = MemoryManager.delete_memory(memory_id=memory_id, db=db)
    if not success:
        raise HTTPException(status_code=404, detail="Memory item not found.")
    return {"status": "success", "deleted_id": memory_id}
