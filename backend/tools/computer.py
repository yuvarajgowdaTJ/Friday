import subprocess
import os
import psutil
import logging
from typing import Dict, Any, List
from backend.tools.registry import tool_registry

logger = logging.getLogger("JARVIS.Tools.Computer")

APP_COMMAND_MAP = {
    "chrome": "start chrome",
    "google chrome": "start chrome",
    "vscode": "code",
    "vs code": "code",
    "notepad": "notepad",
    "calculator": "calc",
    "calc": "calc",
    "explorer": "explorer",
    "terminal": "start cmd",
    "cmd": "start cmd",
    "powershell": "start powershell",
    "edge": "start msedge",
    "microsoft edge": "start msedge",
    "whatsapp": "start whatsapp",
}

@tool_registry.register(
    name="launch_application",
    description="Launches a desktop application on Windows (e.g. 'chrome', 'vscode', 'notepad', 'calculator', 'explorer').",
    parameters={
        "type": "object",
        "properties": {
            "app_name": {
                "type": "string",
                "description": "Name of application or executable command"
            }
        },
        "required": ["app_name"]
    }
)
def launch_application(app_name: str) -> Dict[str, Any]:
    name_clean = app_name.strip().lower()
    cmd = APP_COMMAND_MAP.get(name_clean, name_clean)
    
    try:
        # Validate command or launch subprocess
        if name_clean not in APP_COMMAND_MAP and not os.path.exists(cmd):
            # If application is unknown and not a valid file path, raise FileNotFoundError
            raise FileNotFoundError(f"Application '{app_name}' not found.")

        subprocess.Popen(cmd, shell=True)
        return {
            "app_name": app_name,
            "status": "SUCCESS",
            "message": f"Application '{app_name}' launched successfully.",
            "command": cmd
        }
    except (FileNotFoundError, Exception) as e:
        from backend.core.errors import ToolErrorCategory
        logger.error(f"Failed to launch application '{app_name}': {e}", exc_info=True)
        app_title = app_name.capitalize()
        user_msg = f"{app_title} could not be opened because the application was not found."
        return {
            "status": "ERROR",
            "error_category": ToolErrorCategory.APPLICATION_ERROR.value,
            "app_name": app_name,
            "error": str(e),
            "user_message": user_msg,
            "speech_answer": user_msg
        }

@tool_registry.register(
    name="close_application",
    description="Closes running application processes matching name safely.",
    parameters={
        "type": "object",
        "properties": {
            "app_name": {
                "type": "string",
                "description": "Name of process to terminate (e.g. 'notepad', 'chrome')"
            }
        },
        "required": ["app_name"]
    }
)
def close_application(app_name: str) -> Dict[str, Any]:
    name_clean = app_name.strip().lower()
    terminated_count = 0
    
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            pname = proc.info['name'].lower()
            if name_clean in pname:
                proc.terminate()
                terminated_count += 1
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass

    return {
        "app_name": app_name,
        "terminated_processes": terminated_count,
        "status": f"Terminated {terminated_count} process(es) matching '{app_name}'."
    }

@tool_registry.register(
    name="get_active_window",
    description="Gets list of primary running user application windows.",
    parameters={
        "type": "object",
        "properties": {},
        "required": []
    }
)
def get_active_window() -> Dict[str, Any]:
    running_apps = []
    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_info']):
        try:
            name = proc.info['name']
            if name and name.endswith('.exe') and not name.lower().startswith('svchost'):
                if proc.info['memory_info'] and proc.info['memory_info'].rss > 20 * 1024 * 1024:
                    running_apps.append({
                        "pid": proc.info['pid'],
                        "name": name,
                        "memory_mb": round(proc.info['memory_info'].rss / (1024 * 1024), 1)
                    })
        except Exception:
            pass

    # Sort by top memory usage
    running_apps.sort(key=lambda x: x['memory_mb'], reverse=True)
    return {
        "running_applications": running_apps[:15],
        "count": len(running_apps)
    }
