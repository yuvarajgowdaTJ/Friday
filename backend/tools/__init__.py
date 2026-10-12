# Automatically import all tool modules to register them in ToolRegistry
import backend.tools.browser
import backend.tools.calculator
import backend.tools.computer
import backend.tools.files
import backend.tools.screenshot
import backend.tools.system
import backend.tools.web_intelligence
import backend.vision.screen_analyzer
import backend.core.memory

from backend.tools.registry import tool_registry

__all__ = ["tool_registry"]
