import datetime
import logging
from typing import Dict, Any
from pathlib import Path
from backend.config import SCREENSHOTS_DIR
from backend.tools.registry import tool_registry

logger = logging.getLogger("JARVIS.Tools.Screenshot")

@tool_registry.register(
    name="capture_screenshot",
    description="Captures a full screenshot of the primary desktop display and saves it as an image file.",
    parameters={
        "type": "object",
        "properties": {},
        "required": []
    }
)
def capture_screenshot() -> Dict[str, Any]:
    filename = f"screenshot_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
    filepath = SCREENSHOTS_DIR / filename

    try:
        from PIL import ImageGrab
        img = ImageGrab.grab()
        img.save(filepath)
        return {
            "status": "SUCCESS",
            "filename": filename,
            "filepath": str(filepath),
            "width": img.width,
            "height": img.height
        }
    except Exception as e:
        logger.error(f"Screenshot capture failed: {e}")
        return {
            "status": "ERROR",
            "error": f"Failed to capture screenshot: {str(e)}"
        }
