from backend.tools.registry import tool_registry
import backend.tools.system
import backend.tools.files
from fastapi.testclient import TestClient
from backend.main import app
from backend.database.database import init_db

init_db()
client = TestClient(app)

def test_system_stats_tool():
    res = tool_registry.execute("get_system_stats", {})
    assert res["status"] == "SUCCESS"
    assert "result" in res
    assert "cpu" in res["result"]
    assert "ram" in res["result"]

def test_file_create_and_read():
    test_path = "./data/test_file.txt"
    create_res = tool_registry.execute("create_file", {"path": test_path, "content": "Hello JARVIS test"})
    assert create_res["status"] == "SUCCESS"

    read_res = tool_registry.execute("read_file", {"path": test_path})
    assert read_res["status"] == "SUCCESS"
    assert read_res["result"]["content"] == "Hello JARVIS test"

    del_res = tool_registry.execute("delete_file", {"path": test_path}, bypass_security=True)
    assert del_res["status"] == "SUCCESS"

def test_open_folder_tool():
    res = tool_registry.execute("open_folder", {"folder_name": "downloads"})
    assert res["status"] == "SUCCESS"
    assert "Downloads" in res["result"]["folder"]

def test_tool_audit_endpoint():
    # Execute a tool
    exec_res = client.post("/api/tools/execute", json={"tool_name": "get_system_stats", "arguments": {}})
    assert exec_res.status_code == 200

    # Check audit log endpoint
    audit_res = client.get("/api/tools/audit")
    assert audit_res.status_code == 200
    logs = audit_res.json()
    assert isinstance(logs, list)
    assert len(logs) > 0
    assert any(log["tool_name"] == "get_system_stats" for log in logs)
