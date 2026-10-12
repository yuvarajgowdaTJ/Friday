from backend.core.memory import MemoryManager
from backend.database.database import init_db, SessionLocal
from backend.database.models import MemoryItem
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def _clear_memories():
    db = SessionLocal()
    try:
        db.query(MemoryItem).delete()
        db.commit()
    finally:
        db.close()

def test_memory_crud():
    init_db()
    _clear_memories()
    # Add memory
    res = MemoryManager.add_memory(key="test_language", value="Python 3.11", category="preference")
    assert res["status"] == "stored"
    
    # Search memory
    matches = MemoryManager.search_memories("Python")
    assert len(matches) > 0
    assert any(m["key"] == "test_language" for m in matches)

    # Delete memory
    mem_id = res["id"]
    deleted = MemoryManager.delete_memory(mem_id)
    assert deleted is True

def test_memory_natural_language_sequence():
    init_db()
    _clear_memories()
    # Step 1: Remember
    res1 = client.post("/api/chat", json={"message": "Remember that my favorite programming language is Python"})
    assert res1.status_code == 200
    assert "remembered" in res1.json()["response"].lower() or "python" in res1.json()["response"].lower()

    # Verify stored in SQLite DB
    stored = MemoryManager.search_memories("Python")
    assert len(stored) > 0

    # Step 2: Query memory
    res2 = client.post("/api/chat", json={"message": "What is my favorite programming language?"})
    assert res2.status_code == 200
    assert "python" in res2.json()["response"].lower()

    # Step 3: Forget
    res3 = client.post("/api/chat", json={"message": "Forget that my favorite programming language is Python"})
    assert res3.status_code == 200
    assert "forgotten" in res3.json()["response"].lower() or "removed" in res3.json()["response"].lower()

    # Verify deleted from SQLite DB
    after_del = MemoryManager.search_memories("Python")
    assert len(after_del) == 0
