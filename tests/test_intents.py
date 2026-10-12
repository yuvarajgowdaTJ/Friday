"""
Unit tests for FRIDAY's improved intent classification and routing.
"""

from backend.core.intent import IntentClassifier, Intent
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_intent_classification_required_examples():
    # 1. 1/0 -> calculator
    res1 = IntentClassifier.classify("1/0")
    assert res1["intent"] == Intent.CALCULATOR

    # 2. free fire -> research
    res2 = IntentClassifier.classify("free fire")
    assert res2["intent"] == Intent.RESEARCH

    # 3. naruto -> research
    res3 = IntentClassifier.classify("naruto")
    assert res3["intent"] == Intent.RESEARCH

    # 4. tell me about lion -> research
    res4 = IntentClassifier.classify("tell me about lion")
    assert res4["intent"] == Intent.RESEARCH

    # 5. tell me about u -> self_query (shorthand 'u' -> 'you')
    res5 = IntentClassifier.classify("tell me about u")
    assert res5["intent"] == Intent.SELF_QUERY

    # 6. who are you -> self_query
    res6 = IntentClassifier.classify("who are you")
    assert res6["intent"] == Intent.SELF_QUERY

    # 7. how are you -> conversation
    res7 = IntentClassifier.classify("how are you")
    assert res7["intent"] == Intent.CONVERSATION

    # 8. tell me a story -> creative
    res8 = IntentClassifier.classify("tell me a story")
    assert res8["intent"] == Intent.CREATIVE

    # 9. open whatsapp -> computer_control
    res9 = IntentClassifier.classify("open whatsapp")
    assert res9["intent"] == Intent.COMPUTER_CONTROL

    # 10. take a screenshot -> screenshot
    res10 = IntentClassifier.classify("take a screenshot")
    assert res10["intent"] == Intent.SCREENSHOT

    # 11. what is my CPU usage -> system
    res11 = IntentClassifier.classify("what is my CPU usage")
    assert res11["intent"] == Intent.SYSTEM

def test_division_by_zero_handling():
    res = client.post("/api/chat", json={"message": "1/0"})
    assert res.status_code == 200
    assert any(w in res.json()["response"].lower() for w in ["undefined", "zero"])

def test_shorthand_preserves_original_message():
    res = client.post("/api/chat", json={"message": "tell me about u"})
    assert res.status_code == 200
    # FRIDAY responds about its identity
    assert any(w in res.json()["response"].lower() for w in ["friday", "ai", "intelligence", "assistant"])

def test_open_whatsapp_routing():
    res = client.post("/api/chat", json={"message": "open whatsapp"})
    assert res.status_code == 200
    assert "whatsapp" in res.json()["response"].lower()
