"""
Error classification and handling framework for FRIDAY.
Categorizes errors cleanly without exposing raw stack traces to the user.
"""

import logging
from enum import Enum
from typing import Dict, Any, Optional

logger = logging.getLogger("FRIDAY.Errors")

class ToolErrorCategory(str, Enum):
    INVALID_INPUT = "invalid_input"
    CALCULATION_ERROR = "calculation_error"
    DIVISION_BY_ZERO = "division_by_zero"
    TOOL_UNAVAILABLE = "tool_unavailable"
    PERMISSION_ERROR = "permission_error"
    TIMEOUT = "timeout"
    NETWORK_ERROR = "network_error"
    MODEL_ERROR = "model_error"
    APPLICATION_ERROR = "application_error"
    UNEXPECTED_INTERNAL_ERROR = "unexpected_internal_error"

# Default natural language user-friendly error messages
DEFAULT_USER_MESSAGES: Dict[ToolErrorCategory, str] = {
    ToolErrorCategory.INVALID_INPUT: "The provided input is invalid or improperly formatted, sir.",
    ToolErrorCategory.CALCULATION_ERROR: "I was unable to evaluate that calculation, sir.",
    ToolErrorCategory.DIVISION_BY_ZERO: "I can't divide by zero, sir. Division by zero is undefined.",
    ToolErrorCategory.TOOL_UNAVAILABLE: "The requested tool is currently unavailable.",
    ToolErrorCategory.PERMISSION_ERROR: "I don't have permission to perform that action.",
    ToolErrorCategory.TIMEOUT: "The web search timed out. I can try again.",
    ToolErrorCategory.NETWORK_ERROR: "A network connection error occurred while retrieving external data.",
    ToolErrorCategory.MODEL_ERROR: "The AI model encountered an error generating the response.",
    ToolErrorCategory.APPLICATION_ERROR: "The requested application could not be opened or operated.",
    ToolErrorCategory.UNEXPECTED_INTERNAL_ERROR: "An unexpected internal error occurred. Telemetry has been logged.",
}

class FRIDAYException(Exception):
    """Base exception for FRIDAY containing structured error metadata."""
    def __init__(
        self,
        category: ToolErrorCategory,
        message: str,
        user_message: Optional[str] = None
    ):
        super().__init__(message)
        self.category = category
        self.message = message
        self.user_message = user_message or DEFAULT_USER_MESSAGES.get(category, "An error occurred.")

def format_tool_error(
    category: ToolErrorCategory,
    error_detail: str,
    user_message: Optional[str] = None
) -> Dict[str, Any]:
    """Formats a structured tool error response dictionary."""
    friendly_msg = user_message or DEFAULT_USER_MESSAGES.get(category, "An error occurred.")
    return {
        "status": "ERROR",
        "error_category": category.value,
        "error": error_detail,
        "user_message": friendly_msg,
        "speech_answer": friendly_msg,
        "summary": friendly_msg,
        "result": None
    }
