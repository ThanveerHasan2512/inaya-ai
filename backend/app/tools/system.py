import psutil
import datetime
import shutil
from typing import Dict, Any


def get_system_telemetry() -> Dict[str, Any]:
    """
    Returns real, live system telemetry including CPU, RAM, D: drive disk space, and system uptime.
    """
    try:
        cpu_usage = psutil.cpu_percent(interval=0.1)
        mem = psutil.virtual_memory()
        ram_usage = mem.percent

        # Get D: drive storage
        d_space = shutil.disk_usage("D:\\")
        d_free_gb = round(d_space.free / (1024**3), 2)
        d_total_gb = round(d_space.total / (1024**3), 2)

        # Boot time / uptime
        boot_time = datetime.datetime.fromtimestamp(psutil.boot_time())
        uptime = datetime.datetime.now() - boot_time
        hours, remainder = divmod(int(uptime.total_seconds()), 3600)
        minutes, _ = divmod(remainder, 60)
        uptime_str = f"{hours}h {minutes}m"

        return {
            "success": True,
            "cpu_usage": cpu_usage,
            "ram_usage": ram_usage,
            "d_drive_free_gb": d_free_gb,
            "d_drive_total_gb": d_total_gb,
            "uptime": uptime_str,
            "timestamp": datetime.datetime.now().isoformat(),
        }
    except Exception as exc:
        return {
            "success": False,
            "cpu_usage": 0.0,
            "ram_usage": 0.0,
            "d_drive_free_gb": 0.0,
            "d_drive_total_gb": 0.0,
            "uptime": "unknown",
            "error": str(exc),
            "timestamp": datetime.datetime.now().isoformat(),
        }
