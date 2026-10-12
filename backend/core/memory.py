import logging
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from backend.database.database import SessionLocal
from backend.database.models import MemoryItem
from backend.tools.registry import tool_registry

logger = logging.getLogger("JARVIS.Core.Memory")

class MemoryManager:
    @staticmethod
    def add_memory(key: str, value: str, category: str = "general", db: Optional[Session] = None) -> Dict[str, Any]:
        """Store or update a memory item in SQLite database."""
        close_session = False
        if not db:
            db = SessionLocal()
            close_session = True

        try:
            existing = db.query(MemoryItem).filter(MemoryItem.key.ilike(key)).first()
            if existing:
                existing.value = value
                existing.category = category
                db.commit()
                db.refresh(existing)
                item = existing
            else:
                item = MemoryItem(key=key, value=value, category=category)
                db.add(item)
                db.commit()
                db.refresh(item)

            return {
                "id": item.id,
                "key": item.key,
                "value": item.value,
                "category": item.category,
                "status": "stored"
            }
        finally:
            if close_session:
                db.close()

    @staticmethod
    def get_all_memories(db: Optional[Session] = None) -> List[Dict[str, Any]]:
        """Retrieve all stored memories."""
        close_session = False
        if not db:
            db = SessionLocal()
            close_session = True
        try:
            items = db.query(MemoryItem).all()
            return [
                {
                    "id": item.id,
                    "key": item.key,
                    "value": item.value,
                    "category": item.category,
                    "created_at": item.created_at.isoformat() if item.created_at else None
                }
                for item in items
            ]
        finally:
            if close_session:
                db.close()

    @staticmethod
    def search_memories(query: str, db: Optional[Session] = None) -> List[Dict[str, Any]]:
        """Search memories matching query keyword."""
        close_session = False
        if not db:
            db = SessionLocal()
            close_session = True
        try:
            pattern = f"%{query}%"
            items = (
                db.query(MemoryItem)
                .filter((MemoryItem.key.ilike(pattern)) | (MemoryItem.value.ilike(pattern)))
                .all()
            )
            return [
                {
                    "id": item.id,
                    "key": item.key,
                    "value": item.value,
                    "category": item.category
                }
                for item in items
            ]
        finally:
            if close_session:
                db.close()

    @staticmethod
    def delete_memory(memory_id: int, db: Optional[Session] = None) -> bool:
        """Delete a memory item by ID."""
        close_session = False
        if not db:
            db = SessionLocal()
            close_session = True
        try:
            item = db.query(MemoryItem).filter(MemoryItem.id == memory_id).first()
            if item:
                db.delete(item)
                db.commit()
                return True
            return False
        finally:
            if close_session:
                db.close()

    @staticmethod
    def delete_by_query(query: str, db: Optional[Session] = None) -> List[Dict[str, Any]]:
        """Deletes memories matching query keywords or key/value."""
        import re
        close_session = False
        if not db:
            db = SessionLocal()
            close_session = True
        try:
            clean_q = query.strip().lower()
            all_items = db.query(MemoryItem).all()
            deleted = []
            stop_words = {"the", "that", "and", "for", "with", "this", "what", "about", "forget", "please", "my", "your", "sir"}
            words = [w for w in re.split(r'\s+', clean_q) if len(w) > 2 and w not in stop_words]
            for item in all_items:
                k_low = item.key.lower()
                v_low = item.value.lower()
                matched = False
                if clean_q in k_low or clean_q in v_low or k_low in clean_q or v_low in clean_q:
                    matched = True
                elif any(w in k_low or w in v_low for w in words):
                    matched = True
                
                if matched:
                    deleted.append({"id": item.id, "key": item.key, "value": item.value})
                    db.delete(item)

            if deleted:
                db.commit()
            return deleted
        finally:
            if close_session:
                db.close()

# Register Memory tools with ToolRegistry
@tool_registry.register(
    name="add_memory",
    description="Stores a new fact, preference, or piece of information into permanent memory.",
    parameters={
        "type": "object",
        "properties": {
            "key": {"type": "string", "description": "Subject or attribute (e.g. 'favorite programming language')"},
            "value": {"type": "string", "description": "Value to store (e.g. 'Python')"},
            "category": {"type": "string", "description": "Category (default 'preference')"}
        },
        "required": ["key", "value"]
    }
)
def tool_add_memory(key: str, value: str, category: str = "preference") -> Dict[str, Any]:
    item = MemoryManager.add_memory(key, value, category)
    return {"status": "SUCCESS", "memory": item, "message": f"Saved {key} = {value} in memory archives."}

@tool_registry.register(
    name="delete_memory",
    description="Deletes or forgets a stored memory or preference by keyword or subject.",
    parameters={
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "Topic, key, or value to forget (e.g. 'favorite programming language', 'Python')"}
        },
        "required": ["query"]
    }
)
def tool_delete_memory(query: str) -> Dict[str, Any]:
    deleted = MemoryManager.delete_by_query(query)
    if deleted:
        return {
            "status": "SUCCESS",
            "deleted_count": len(deleted),
            "deleted_items": deleted,
            "message": f"I have forgotten and removed {len(deleted)} matching item(s) from my archives."
        }
    return {
        "status": "SUCCESS",
        "deleted_count": 0,
        "deleted_items": [],
        "message": f"I searched my archives, but found no memory matching '{query}' to forget."
    }

@tool_registry.register(
    name="get_memories",
    description="Retrieves stored long-term memories and user preferences.",
    parameters={
        "type": "object",
        "properties": {},
        "required": []
    }
)
def tool_get_memories() -> Dict[str, Any]:
    items = MemoryManager.get_all_memories()
    return {"status": "SUCCESS", "memories": items, "count": len(items)}

@tool_registry.register(
    name="search_memories",
    description="Searches stored memories for a keyword or question.",
    parameters={
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "Keyword to search memories"}
        },
        "required": ["query"]
    }
)
def tool_search_memories(query: str) -> Dict[str, Any]:
    items = MemoryManager.search_memories(query)
    return {"status": "SUCCESS", "query": query, "matches": items, "count": len(items)}

