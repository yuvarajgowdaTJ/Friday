from backend.core.brain import JarvisBrain

def test_brain_offline_response():
    brain = JarvisBrain(api_key="")
    response = brain.generate_response([{"role": "user", "content": "Hello Jarvis"}])
    assert response is not None
    assert "content" in response
    assert response["mode"] == "offline"
    assert any(name in response["content"].lower() for name in ["friday", "jarvis"])

def test_brain_python_query():
    brain = JarvisBrain(api_key="")
    response = brain.generate_response([{"role": "user", "content": "What is Python?"}])
    assert "python" in response["content"].lower()
