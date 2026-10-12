import psutil
import platform
import socket
import logging
from typing import Dict, Any
from backend.tools.registry import tool_registry

logger = logging.getLogger("JARVIS.Tools.System")

@tool_registry.register(
    name="get_system_stats",
    description="Retrieves live system hardware metrics (CPU percentage, RAM usage, Disk space, Battery status, Network connectivity).",
    parameters={
        "type": "object",
        "properties": {},
        "required": []
    }
)
def get_system_stats() -> Dict[str, Any]:
    # CPU
    cpu_pct = psutil.cpu_percent(interval=0.1)
    cpu_count = psutil.cpu_count(logical=True)

    # Memory
    mem = psutil.virtual_memory()

    # Disk
    disk = psutil.disk_usage('/')

    # Battery
    battery_info = None
    try:
        bat = psutil.sensors_battery()
        if bat:
            battery_info = {
                "percent": bat.percent,
                "power_plugged": bat.power_plugged,
                "secs_left": bat.secsleft
            }
    except Exception:
        pass

    # Network check
    network_online = False
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=2)
        network_online = True
    except Exception:
        pass

    return {
        "status": "OPERATIONAL",
        "os": f"{platform.system()} {platform.release()}",
        "architecture": platform.machine(),
        "cpu": {
            "percent": cpu_pct,
            "cores": cpu_count
        },
        "ram": {
            "percent": mem.percent,
            "used_gb": round(mem.used / (1024 ** 3), 2),
            "total_gb": round(mem.total / (1024 ** 3), 2)
        },
        "disk": {
            "percent": disk.percent,
            "free_gb": round(disk.free / (1024 ** 3), 2),
            "total_gb": round(disk.total / (1024 ** 3), 2)
        },
        "battery": battery_info,
        "network": {
            "online": network_online,
            "hostname": socket.gethostname()
        }
    }
