import logging
import inspect
from typing import Dict, Any, Callable, List, Optional, Tuple
from backend.core.security import SecurityEngine, SecurityLevel

logger = logging.getLogger("JARVIS.Tools")

class Tool:
    def __init__(self, name: str, description: str, func: Callable, parameters: Dict[str, Any]):
        self.name = name
        self.description = description
        self.func = func
        self.parameters = parameters

    def to_openai_schema(self) -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters
            }
        }

class ToolRegistry:
    def __init__(self):
        self._tools: Dict[str, Tool] = {}

    def register(self, name: str, description: str, parameters: Dict[str, Any]):
        """Decorator to register a tool function."""
        def decorator(func: Callable):
            tool = Tool(name=name, description=description, func=func, parameters=parameters)
            self._tools[name] = tool
            logger.info(f"Registered tool: {name}")
            return func
        return decorator

    def get_tool(self, name: str) -> Optional[Tool]:
        return self._tools.get(name)

    def list_tools(self) -> List[Dict[str, Any]]:
        return [
            {
                "name": t.name,
                "description": t.description,
                "parameters": t.parameters
            }
            for t in self._tools.values()
        ]

    def get_openai_schemas(self) -> List[Dict[str, Any]]:
        return [t.to_openai_schema() for t in self._tools.values()]

    def execute(self, name: str, args: Dict[str, Any], bypass_security: bool = False) -> Dict[str, Any]:
        """
        Executes a registered tool after security validation.
        """
        tool = self.get_tool(name)
        if not tool:
            from backend.core.errors import ToolErrorCategory, DEFAULT_USER_MESSAGES
            return {
                "status": "ERROR",
                "error_category": ToolErrorCategory.TOOL_UNAVAILABLE.value,
                "tool_name": name,
                "arguments": args,
                "error": f"Tool '{name}' is not registered.",
                "user_message": DEFAULT_USER_MESSAGES[ToolErrorCategory.TOOL_UNAVAILABLE],
                "result": None
            }

        # Security evaluation
        sec_level, sec_msg = SecurityEngine.evaluate_tool_call(name, args)

        if sec_level == SecurityLevel.BLOCKED:
            from backend.core.errors import ToolErrorCategory, DEFAULT_USER_MESSAGES
            return {
                "status": "BLOCKED",
                "error_category": ToolErrorCategory.PERMISSION_ERROR.value,
                "security_level": sec_level.value,
                "tool_name": name,
                "arguments": args,
                "error": sec_msg,
                "user_message": DEFAULT_USER_MESSAGES[ToolErrorCategory.PERMISSION_ERROR],
                "result": None
            }

        if sec_level == SecurityLevel.CONFIRMATION_REQUIRED and not bypass_security:
            return {
                "status": "CONFIRMATION_REQUIRED",
                "security_level": sec_level.value,
                "message": sec_msg,
                "tool_name": name,
                "arguments": args,
                "result": None
            }

        try:
            res = tool.func(**args)
            # If tool function itself returned a dict with status == "ERROR", ensure error_category is present
            if isinstance(res, dict) and res.get("status") == "ERROR":
                from backend.core.errors import ToolErrorCategory, DEFAULT_USER_MESSAGES
                cat = res.get("error_category") or ToolErrorCategory.CALCULATION_ERROR.value
                user_msg = res.get("user_message") or res.get("speech_answer") or res.get("summary") or DEFAULT_USER_MESSAGES.get(ToolErrorCategory(cat), "Tool error.")
                return {
                    "status": "ERROR",
                    "error_category": cat,
                    "security_level": sec_level.value,
                    "tool_name": name,
                    "arguments": args,
                    "error": res.get("error") or user_msg,
                    "user_message": user_msg,
                    "result": res
                }
            return {
                "status": "SUCCESS",
                "security_level": sec_level.value,
                "tool_name": name,
                "arguments": args,
                "result": res,
                "error": None
            }
        except Exception as e:
            # Detailed stack trace remains in developer logs
            logger.error(f"Error executing tool '{name}': {e}", exc_info=True)
            from backend.core.errors import ToolErrorCategory, DEFAULT_USER_MESSAGES
            
            # Map exception types to categories
            if isinstance(e, ZeroDivisionError):
                cat = ToolErrorCategory.DIVISION_BY_ZERO
            elif isinstance(e, PermissionError):
                cat = ToolErrorCategory.PERMISSION_ERROR
            elif isinstance(e, (TimeoutError, Exception)) and "timeout" in str(e).lower():
                cat = ToolErrorCategory.TIMEOUT
            elif isinstance(e, FileNotFoundError):
                cat = ToolErrorCategory.APPLICATION_ERROR
            elif isinstance(e, (ValueError, SyntaxError, TypeError)):
                cat = ToolErrorCategory.INVALID_INPUT
            else:
                cat = ToolErrorCategory.UNEXPECTED_INTERNAL_ERROR

            user_msg = DEFAULT_USER_MESSAGES.get(cat, "An unexpected tool error occurred.")
            if isinstance(e, FileNotFoundError) and args.get("app_name"):
                app_n = str(args.get("app_name")).capitalize()
                user_msg = f"{app_n} could not be opened because the application was not found."

            return {
                "status": "ERROR",
                "error_category": cat.value,
                "security_level": sec_level.value,
                "tool_name": name,
                "arguments": args,
                "error": str(e),
                "user_message": user_msg,
                "result": None
            }

tool_registry = ToolRegistry()
