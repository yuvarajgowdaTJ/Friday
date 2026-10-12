import webbrowser
import logging
from typing import Dict, Any
from backend.tools.registry import tool_registry

logger = logging.getLogger("JARVIS.Tools.Browser")

@tool_registry.register(
    name="open_browser",
    description="Opens default web browser or specified URL on the user's desktop.",
    parameters={
        "type": "object",
        "properties": {
            "url": {
                "type": "string",
                "description": "URL to open in browser (e.g. 'https://google.com'). Defaults to google.com."
            }
        },
        "required": []
    }
)
def open_browser(url: str = "https://google.com") -> Dict[str, Any]:
    if not url.startswith("http://") and not url.startswith("https://"):
        url = "https://" + url
    webbrowser.open(url)
    return {"opened_url": url, "status": f"Opened {url} in web browser."}

@tool_registry.register(
    name="open_url",
    description="Alias for opening a specific web URL.",
    parameters={
        "type": "object",
        "properties": {
            "url": {"type": "string", "description": "Web URL to open"}
        },
        "required": ["url"]
    }
)
def open_url(url: str) -> Dict[str, Any]:
    return open_browser(url)
