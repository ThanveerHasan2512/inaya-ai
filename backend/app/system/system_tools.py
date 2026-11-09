import os
import psutil
import shutil
import platform
import datetime
from typing import Dict, Any, List


def get_system_telemetry() -> Dict[str, Any]:
    """
    Returns live system telemetry: CPU, RAM, D: drive, system uptime, and battery.
    """
    try:
        cpu_usage = psutil.cpu_percent(interval=0.1)
        mem = psutil.virtual_memory()
        ram_usage = mem.percent

        # Disk storage for D: and C:
        d_space = shutil.disk_usage("D:\\")
        d_free_gb = round(d_space.free / (1024**3), 2)
        d_total_gb = round(d_space.total / (1024**3), 2)

        # Boot time / uptime
        boot_time = datetime.datetime.fromtimestamp(psutil.boot_time())
        uptime = datetime.datetime.now() - boot_time
        hours, remainder = divmod(int(uptime.total_seconds()), 3600)
        minutes, _ = divmod(remainder, 60)
        uptime_str = f"{hours}h {minutes}m"

        # Battery info
        battery = psutil.sensors_battery()
        battery_info = {
            "percent": battery.percent if battery else 100,
            "power_plugged": battery.power_plugged if battery else True,
            "secsleft": battery.secsleft if battery else -1,
        }

        return {
            "success": True,
            "action": "get_system_telemetry",
            "cpu_usage": cpu_usage,
            "ram_usage": ram_usage,
            "d_drive_free_gb": d_free_gb,
            "d_drive_total_gb": d_total_gb,
            "uptime": uptime_str,
            "battery": battery_info,
            "verification_status": "verified",
            "verification_details": {"cpu": cpu_usage, "ram": ram_usage},
            "details": f"CPU: {cpu_usage}%, RAM: {ram_usage}%, D: Drive Free: {d_free_gb} GB / {d_total_gb} GB, Uptime: {uptime_str}.",
            "timestamp": datetime.datetime.now().isoformat(),
        }
    except Exception as exc:
        return {
            "success": False,
            "action": "get_system_telemetry",
            "cpu_usage": 0.0,
            "ram_usage": 0.0,
            "d_drive_free_gb": 0.0,
            "d_drive_total_gb": 0.0,
            "uptime": "unknown",
            "error": str(exc),
            "verification_status": "failed",
            "timestamp": datetime.datetime.now().isoformat(),
        }


def get_system_info() -> Dict[str, Any]:
    """
    Returns static and architectural information about this Windows PC.
    """
    try:
        mem = psutil.virtual_memory()
        total_ram_gb = round(mem.total / (1024**3), 2)
        d_space = shutil.disk_usage("D:\\")
        c_space = shutil.disk_usage("C:\\")

        info = {
            "os": platform.system(),
            "os_release": platform.release(),
            "os_version": platform.version(),
            "machine": platform.machine(),
            "processor": platform.processor(),
            "node_name": platform.node(),
            "total_ram_gb": total_ram_gb,
            "c_drive_total_gb": round(c_space.total / (1024**3), 2),
            "d_drive_total_gb": round(d_space.total / (1024**3), 2),
            "python_version": platform.python_version(),
        }

        return {
            "success": True,
            "action": "get_system_info",
            "system_info": info,
            "verification_status": "verified",
            "details": f"Windows PC '{info['node_name']}' running {info['os']} {info['os_release']} ({info['machine']}) with {total_ram_gb} GB RAM.",
            "error": None,
        }
    except Exception as exc:
        return {"success": False, "action": "get_system_info", "error": str(exc), "verification_status": "failed"}


def get_running_processes(limit: int = 15) -> Dict[str, Any]:
    """
    Returns top active processes by memory usage.
    """
    try:
        processes = []
        for p in psutil.process_iter(['pid', 'name', 'memory_percent', 'cpu_percent']):
            try:
                processes.append({
                    "pid": p.info['pid'],
                    "name": p.info['name'],
                    "ram_percent": round(p.info['memory_percent'] or 0.0, 1),
                })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        # Sort by RAM usage descending
        processes.sort(key=lambda x: x["ram_percent"], reverse=True)
        top = processes[:limit]

        return {
            "success": True,
            "action": "get_running_processes",
            "total_processes": len(processes),
            "top_processes": top,
            "verification_status": "verified",
            "details": f"Retrieved top {len(top)} active processes by memory consumption.",
            "error": None,
        }
    except Exception as exc:
        return {"success": False, "action": "get_running_processes", "error": str(exc), "verification_status": "failed"}
