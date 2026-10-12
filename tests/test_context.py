"""
Unit tests for FRIDAY's lightweight conversation context, pronoun resolution, and topic tracking.
"""

from fastapi.testclient import TestClient
from backend.main import app
from backend.core.agent_router import NaturalLanguageAgent, SESSION_CONTEXT

client = TestClient(app)

def test_pronoun_reference_resolution():
    session_id = "test_pronoun_session"
    if session_id in SESSION_CONTEXT:
        del SESSION_CONTEXT[session_id]

    # Turn 1: Tell me about Naruto
    res1 = client.post("/api/chat", json={"message": "Tell me about Naruto.", "session_id": session_id})
    assert res1.status_code == 200
    ctx = NaturalLanguageAgent.get_session_context(session_id)
    assert ctx["last_topic"].lower() == "naruto"

    # Turn 2: Who created it?
    res2 = client.post("/api/chat", json={"message": "Who created it?", "session_id": session_id})
    assert res2.status_code == 200
    assert any(w in res2.json()["response"].lower() for w in ["kishimoto", "masashi", "naruto", "author", "creator"])

def test_follow_up_browser_search():
    session_id = "test_browser_session"
    if session_id in SESSION_CONTEXT:
        del SESSION_CONTEXT[session_id]

    # Turn 1: Open Chrome
    res1 = client.post("/api/chat", json={"message": "Open Chrome.", "session_id": session_id})
    assert res1.status_code == 200
    assert "chrome" in res1.json()["response"].lower()

    # Turn 2: Search for NVIDIA
    res2 = client.post("/api/chat", json={"message": "Search for NVIDIA.", "session_id": session_id})
    assert res2.status_code == 200
    assert "nvidia" in res2.json()["response"].lower()

def test_topic_continuation():
    session_id = "test_continuation_session"
    if session_id in SESSION_CONTEXT:
        del SESSION_CONTEXT[session_id]

    # Turn 1: Tell me about Naruto
    res1 = client.post("/api/chat", json={"message": "Tell me about Naruto.", "session_id": session_id})
    assert res1.status_code == 200

    # Turn 2: What about its main character?
    res2 = client.post("/api/chat", json={"message": "What about its main character?", "session_id": session_id})
    assert res2.status_code == 200
    assert any(w in res2.json()["response"].lower() for w in ["naruto", "uzumaki", "character", "ninja"])

def test_topic_change_safeguard():
    session_id = "test_topic_change_session"
    if session_id in SESSION_CONTEXT:
        del SESSION_CONTEXT[session_id]

    # Turn 1: Tell me about Naruto
    res1 = client.post("/api/chat", json={"message": "Tell me about Naruto.", "session_id": session_id})
    assert res1.status_code == 200

    # Turn 2: What is the capital of France? (Explicit new topic)
    res2 = client.post("/api/chat", json={"message": "What is the capital of France?", "session_id": session_id})
    assert res2.status_code == 200
    assert "paris" in res2.json()["response"].lower() or "france" in res2.json()["response"].lower()
    
    ctx = NaturalLanguageAgent.get_session_context(session_id)
    # Verify topic updated to France / capital of France and does NOT hold Naruto
    assert "naruto" not in ctx["last_topic"].lower()

def test_tool_math_follow_up():
    session_id = "test_math_followup_session"
    if session_id in SESSION_CONTEXT:
        del SESSION_CONTEXT[session_id]

    # Turn 1: What is 10 multiplied by 5?
    res1 = client.post("/api/chat", json={"message": "What is 10 multiplied by 5?", "session_id": session_id})
    assert res1.status_code == 200
    assert "50" in res1.json()["response"]

    # Turn 2: Now divide it by 5.
    res2 = client.post("/api/chat", json={"message": "Now divide it by 5.", "session_id": session_id})
    assert res2.status_code == 200
    assert "10" in res2.json()["response"]
