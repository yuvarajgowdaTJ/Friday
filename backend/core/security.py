from enum import Enum
from typing import Dict, Any, Tuple

class SecurityLevel(str, Enum):
    SAFE = "SAFE"
    CONFIRMATION_REQUIRED = "CONFIRMATION_REQUIRED"
    BLOCKED = "BLOCKED"

# Tool Classification Mapping
TOOL_SECURITY_POLICIES = {
    # System & Info (SAFE)
    "get_system_stats": SecurityLevel.SAFE,
    "get_active_window": SecurityLevel.SAFE,
    "capture_screenshot": SecurityLevel.SAFE,
    "search_files": SecurityLevel.SAFE,
    "list_directory": SecurityLevel.SAFE,
    "read_file": SecurityLevel.SAFE,
    "web_search": SecurityLevel.SAFE,
    "open_browser": SecurityLevel.SAFE,
    "open_folder": SecurityLevel.SAFE,
    "calculate": SecurityLevel.SAFE,
    "analyze_screen": SecurityLevel.SAFE,
    "find_largest_files": SecurityLevel.SAFE,
    "search_memories": SecurityLevel.SAFE,
    "get_memories": SecurityLevel.SAFE,
    "add_memory": SecurityLevel.SAFE,
    "delete_memory": SecurityLevel.SAFE,
    
    # Computer execution (SAFE for basic apps, CONFIRMATION for custom commands)
    "launch_application": SecurityLevel.SAFE,
    "create_directory": SecurityLevel.SAFE,
    "create_file": SecurityLevel.SAFE,
    
    # Destructive or System mutating actions (CONFIRMATION_REQUIRED)
    "delete_file": SecurityLevel.CONFIRMATION_REQUIRED,
    "rename_file": SecurityLevel.CONFIRMATION_REQUIRED,
    "move_file": SecurityLevel.CONFIRMATION_REQUIRED,
    "close_application": SecurityLevel.CONFIRMATION_REQUIRED,
    "execute_terminal": SecurityLevel.CONFIRMATION_REQUIRED,
}

# Forbidden keywords for BLOCKED status
BLOCKED_PATTERNS = [
    "format c:",
    "rm -rf /",
    "del /s /q c:\\",
    "shutdown /s",
    "reg delete",
    "net user",
]

class SecurityEngine:
    @staticmethod
    def evaluate_tool_call(tool_name: str, args: Dict[str, Any]) -> Tuple[SecurityLevel, str]:
        """
        Evaluates tool call safety level.
        Returns (SecurityLevel, message).
        """
        # Check blocked patterns in command or arguments
        args_str = str(args).lower()
        for pattern in BLOCKED_PATTERNS:
            if pattern in args_str:
                return SecurityLevel.BLOCKED, f"Operation blocked for security reasons (Forbidden pattern: '{pattern}')"

        policy = TOOL_SECURITY_POLICIES.get(tool_name, SecurityLevel.CONFIRMATION_REQUIRED)
        
        if policy == SecurityLevel.SAFE:
            return SecurityLevel.SAFE, "Execution pre-approved."
        elif policy == SecurityLevel.CONFIRMATION_REQUIRED:
            return SecurityLevel.CONFIRMATION_REQUIRED, f"Action '{tool_name}' requires explicit user confirmation before proceeding."
        else:
            return SecurityLevel.BLOCKED, "Action blocked by security policy."
