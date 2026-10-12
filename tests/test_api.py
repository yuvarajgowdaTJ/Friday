from fastapi.testclient import TestClient
from backend.main import app
from backend.database.database import init_db

init_db()
client = TestClient(app)

def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["app"] in ["FRIDAY", "JARVIS"]

def test_test1_hello():
    res = client.post("/api/chat", json={"message": "hello"})
    assert res.status_code == 200
    ans = res.json()["response"].lower()
    assert any(g in ans for g in ["good day", "service", "assist", "operational", "jarvis"])

def test_test2_coffee_research():
    res = client.post("/api/chat", json={"message": "Tell me about coffee."})
    assert res.status_code == 200
    ans = res.json()["response"].lower()
    assert "coffee" in ans
    assert any(w in ans for w in ["beverage", "bean", "caffeine", "roast"])

def test_test3_math_multiplication():
    res = client.post("/api/chat", json={"message": "What is 8 multiplied by 6?"})
    assert res.status_code == 200
    ans = res.json()["response"]
    assert "48" in ans

def test_math_variations():
    # 125 divided by 5
    res1 = client.post("/api/chat", json={"message": "What is 125 divided by 5?"})
    assert "25" in res1.json()["response"]

    # 27 squared
    res2 = client.post("/api/chat", json={"message": "Calculate 27 squared."})
    assert "729" in res2.json()["response"]

    # 15% of 800
    res3 = client.post("/api/chat", json={"message": "What is 15% of 800?"})
    assert "120" in res3.json()["response"]

    # Add 45 and 72
    res4 = client.post("/api/chat", json={"message": "Add 45 and 72."})
    assert "117" in res4.json()["response"]

def test_test4_open_chrome():
    res = client.post("/api/chat", json={"message": "Open Chrome."})
    assert res.status_code == 200
    assert "chrome" in res.json()["response"].lower()

def test_test5_open_calculator():
    res = client.post("/api/chat", json={"message": "Open Calculator."})
    assert res.status_code == 200
    assert "calculator" in res.json()["response"].lower()

def test_test6_cpu_usage():
    res = client.post("/api/chat", json={"message": "What is my CPU usage?"})
    assert res.status_code == 200
    assert "cpu" in res.json()["response"].lower()

def test_test7_open_downloads():
    res = client.post("/api/chat", json={"message": "Open my Downloads folder."})
    assert res.status_code == 200
    assert "downloads" in res.json()["response"].lower()

def test_test8_screenshot():
    res = client.post("/api/chat", json={"message": "Take a screenshot."})
    assert res.status_code == 200
    assert "screenshot" in res.json()["response"].lower()

def test_test9_what_is_on_my_screen():
    res = client.post("/api/chat", json={"message": "What is on my screen?"})
    assert res.status_code == 200
    assert "screen" in res.json()["response"].lower()

def test_test10_11_12_memory_lifecycle():
    # 10: Remember
    res1 = client.post("/api/chat", json={"message": "Remember that my favorite programming language is Python."})
    assert res1.status_code == 200
    assert "python" in res1.json()["response"].lower()

    # 11: Recall
    res2 = client.post("/api/chat", json={"message": "What is my favorite programming language?"})
    assert res2.status_code == 200
    assert "python" in res2.json()["response"].lower()

    # 12: Forget (flexible phrasing without saying 'python')
    res3 = client.post("/api/chat", json={"message": "Forget my favorite programming language."})
    assert res3.status_code == 200
    assert any(w in res3.json()["response"].lower() for w in ["forgotten", "removed"])

def test_test13_find_pdf_count():
    res = client.post("/api/chat", json={"message": "Find my PDF files and tell me how many there are."})
    assert res.status_code == 200
    assert "pdf" in res.json()["response"].lower()

def test_test14_nvidia_news():
    res = client.post("/api/chat", json={"message": "Tell me the latest news about NVIDIA."})
    assert res.status_code == 200
    assert "nvidia" in res.json()["response"].lower()

def test_test15_quantum_computing():
    res = client.post("/api/chat", json={"message": "Explain quantum computing to me like I'm a beginner."})
    assert res.status_code == 200
    ans = res.json()["response"].lower()
    assert "quantum" in ans
    assert any(w in ans for w in ["qubit", "classical", "mechanics"])

def test_conversational_questions():
    # Why is the sky blue?
    res1 = client.post("/api/chat", json={"message": "Why is the sky blue?"})
    assert "scattering" in res1.json()["response"].lower() or "blue" in res1.json()["response"].lower()

    # Compare Python and Java
    res2 = client.post("/api/chat", json={"message": "Compare Python and Java."})
    assert "python" in res2.json()["response"].lower()
    assert "java" in res2.json()["response"].lower()

    # Which is your favorite language?
    res3 = client.post("/api/chat", json={"message": "Which is your favorite language?"})
    assert "python" in res3.json()["response"].lower() or "language" in res3.json()["response"].lower()
