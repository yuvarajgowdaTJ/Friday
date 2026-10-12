from backend.core.security import SecurityEngine, SecurityLevel

def test_security_safe_tool():
    level, msg = SecurityEngine.evaluate_tool_call("get_system_stats", {})
    assert level == SecurityLevel.SAFE

def test_security_confirmation_tool():
    level, msg = SecurityEngine.evaluate_tool_call("delete_file", {"path": "important.txt"})
    assert level == SecurityLevel.CONFIRMATION_REQUIRED

def test_security_blocked_tool():
    level, msg = SecurityEngine.evaluate_tool_call("execute_terminal", {"cmd": "rm -rf /"})
    assert level == SecurityLevel.BLOCKED
