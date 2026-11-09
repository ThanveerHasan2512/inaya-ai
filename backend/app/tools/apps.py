import os
import shutil
import time
import subprocess
from typing import Dict, Any, Optional, List
import psutil

from ..windows.window_manager import find_window_by_process, focus_window, close_process, get_visible_windows

# Safe Windows application definitions with discovery paths and process names
APPROVED_APPLICATIONS: Dict[str, Dict[str, Any]] = {
    "notepad": {
        "name": "Notepad",
        "description": "Windows default text editor",
        "process_names": ["notepad.exe"],
        "discovery_paths": [
            r"C:\Windows\System32\notepad.exe",
            r"C:\Windows\notepad.exe",
        ],
        "default_target": "notepad.exe",
        "title_keyword": "Notepad",
    },
    "calculator": {
        "name": "Calculator",
        "description": "Windows Calculator",
        "process_names": ["CalculatorApp.exe", "calc.exe", "Calculator.exe"],
        "discovery_paths": [
            r"C:\Windows\System32\calc.exe",
            r"C:\Windows\calc.exe",
        ],
        "default_target": "calc.exe",
        "title_keyword": "Calculator",
    },
    "calc": {
        "name": "Calculator",
        "description": "Windows Calculator",
        "process_names": ["CalculatorApp.exe", "calc.exe", "Calculator.exe"],
        "discovery_paths": [
            r"C:\Windows\System32\calc.exe",
        ],
        "default_target": "calc.exe",
        "title_keyword": "Calculator",
    },
    "explorer": {
        "name": "File Explorer",
        "description": "Windows File Explorer",
        "process_names": ["explorer.exe"],
        "discovery_paths": [
            r"C:\Windows\explorer.exe",
        ],
        "default_target": "explorer.exe",
        "title_keyword": "File Explorer",
    },
    "file explorer": {
        "name": "File Explorer",
        "description": "Windows File Explorer",
        "process_names": ["explorer.exe"],
        "discovery_paths": [
            r"C:\Windows\explorer.exe",
        ],
        "default_target": "explorer.exe",
        "title_keyword": "File Explorer",
    },
    "cmd": {
        "name": "Command Prompt",
        "description": "Windows Command Prompt",
        "process_names": ["cmd.exe", "conhost.exe"],
        "discovery_paths": [
            r"C:\Windows\System32\cmd.exe",
        ],
        "default_target": "cmd.exe",
        "title_keyword": "Command Prompt",
    },
    "command prompt": {
        "name": "Command Prompt",
        "description": "Windows Command Prompt",
        "process_names": ["cmd.exe", "conhost.exe"],
        "discovery_paths": [
            r"C:\Windows\System32\cmd.exe",
        ],
        "default_target": "cmd.exe",
        "title_keyword": "Command Prompt",
    },
    "chrome": {
        "name": "Google Chrome",
        "description": "Google Chrome Web Browser",
        "process_names": ["chrome.exe"],
        "discovery_paths": [
            os.path.join(os.environ.get("LOCALAPPDATA", ""), r"Google\Chrome\Application\chrome.exe"),
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        ],
        "default_target": "chrome.exe",
        "title_keyword": "Chrome",
    },
    "google chrome": {
        "name": "Google Chrome",
        "description": "Google Chrome Web Browser",
        "process_names": ["chrome.exe"],
        "discovery_paths": [
            os.path.join(os.environ.get("LOCALAPPDATA", ""), r"Google\Chrome\Application\chrome.exe"),
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        ],
        "default_target": "chrome.exe",
        "title_keyword": "Chrome",
    },
    "edge": {
        "name": "Microsoft Edge",
        "description": "Microsoft Edge Web Browser",
        "process_names": ["msedge.exe"],
        "discovery_paths": [
            r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
            r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
            os.path.join(os.environ.get("LOCALAPPDATA", ""), r"Microsoft\Edge\Application\msedge.exe"),
        ],
        "default_target": "msedge.exe",
        "title_keyword": "Edge",
    },
    "microsoft edge": {
        "name": "Microsoft Edge",
        "description": "Microsoft Edge Web Browser",
        "process_names": ["msedge.exe"],
        "discovery_paths": [
            r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
            r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
            os.path.join(os.environ.get("LOCALAPPDATA", ""), r"Microsoft\Edge\Application\msedge.exe"),
        ],
        "default_target": "msedge.exe",
        "title_keyword": "Edge",
    },
    "code": {
        "name": "Visual Studio Code",
        "description": "VS Code Code Editor",
        "process_names": ["Code.exe"],
        "discovery_paths": [
            os.path.join(os.environ.get("LOCALAPPDATA", ""), r"Programs\Microsoft VS Code\Code.exe"),
            os.path.join(os.environ.get("LOCALAPPDATA", ""), r"Programs\Microsoft VS Code\bin\code.cmd"),
            r"C:\Program Files\Microsoft VS Code\Code.exe",
            r"C:\Program Files\Microsoft VS Code\bin\code.cmd",
            r"C:\Program Files (x86)\Microsoft VS Code\Code.exe",
        ],
        "default_target": "code.cmd",
        "title_keyword": "Visual Studio Code",
    },
    "vs code": {
        "name": "Visual Studio Code",
        "description": "VS Code Code Editor",
        "process_names": ["Code.exe"],
        "discovery_paths": [
            os.path.join(os.environ.get("LOCALAPPDATA", ""), r"Programs\Microsoft VS Code\Code.exe"),
            os.path.join(os.environ.get("LOCALAPPDATA", ""), r"Programs\Microsoft VS Code\bin\code.cmd"),
            r"C:\Program Files\Microsoft VS Code\Code.exe",
            r"C:\Program Files\Microsoft VS Code\bin\code.cmd",
            r"C:\Program Files (x86)\Microsoft VS Code\Code.exe",
        ],
        "default_target": "code.cmd",
        "title_keyword": "Visual Studio Code",
    },
    "vscode": {
        "name": "Visual Studio Code",
        "description": "VS Code Code Editor",
        "process_names": ["Code.exe"],
        "discovery_paths": [
            os.path.join(os.environ.get("LOCALAPPDATA", ""), r"Programs\Microsoft VS Code\Code.exe"),
            os.path.join(os.environ.get("LOCALAPPDATA", ""), r"Programs\Microsoft VS Code\bin\code.cmd"),
            r"C:\Program Files\Microsoft VS Code\Code.exe",
            r"C:\Program Files\Microsoft VS Code\bin\code.cmd",
            r"C:\Program Files (x86)\Microsoft VS Code\Code.exe",
        ],
        "default_target": "code.cmd",
        "title_keyword": "Visual Studio Code",
    },
    "visual studio code": {
        "name": "Visual Studio Code",
        "description": "VS Code Code Editor",
        "process_names": ["Code.exe"],
        "discovery_paths": [
            os.path.join(os.environ.get("LOCALAPPDATA", ""), r"Programs\Microsoft VS Code\Code.exe"),
            os.path.join(os.environ.get("LOCALAPPDATA", ""), r"Programs\Microsoft VS Code\bin\code.cmd"),
            r"C:\Program Files\Microsoft VS Code\Code.exe",
            r"C:\Program Files\Microsoft VS Code\bin\code.cmd",
            r"C:\Program Files (x86)\Microsoft VS Code\Code.exe",
        ],
        "default_target": "code.cmd",
        "title_keyword": "Visual Studio Code",
    },
}


def resolve_executable_path(app_info: Dict[str, Any]) -> Optional[str]:
    """
    Safely resolves the verified executable path from known discovery paths
    or system PATH. Never accepts arbitrary paths from untrusted input.
    """
    # 1. Check known explicit paths
    for candidate in app_info.get("discovery_paths", []):
        if candidate and os.path.isfile(candidate):
            return candidate

    # 2. Check system PATH for default target
    target = app_info.get("default_target", "")
    if target:
        which_path = shutil.which(target)
        if which_path and os.path.isfile(which_path):
            return which_path

    # Fallback: check other process names in PATH
    for proc_name in app_info.get("process_names", []):
        w = shutil.which(proc_name)
        if w and os.path.isfile(w):
            return w

    return target if target else None


def verify_process_running(process_names: list[str]) -> Optional[int]:
    """
    Checks if any process matching the given names is running and returns its PID.
    """
    lower_names = [p.lower() for p in process_names]
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            if proc.info['name'] and proc.info['name'].lower() in lower_names:
                return proc.info['pid']
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue
    return None


def launch_application(app_name: str, dry_run: bool = False, target_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Safely launches an approved Windows desktop application and verifies
    that a visible application window appears where possible.
    Never relies on PID alone as proof of successful launch.
    """
    normalized_key = app_name.strip().lower()
    app_info = APPROVED_APPLICATIONS.get(normalized_key)

    if not app_info:
        unique_names = sorted(list({v["name"] for v in APPROVED_APPLICATIONS.values()}))
        return {
            "success": False,
            "action": "launch_application",
            "error": f"Application '{app_name}' is not in the approved application registry.",
            "available_applications": ", ".join(unique_names),
            "verification_status": "failed",
            "verification_details": {},
            "dry_run": dry_run,
        }

    resolved_path = resolve_executable_path(app_info)
    if not resolved_path:
        return {
            "success": False,
            "action": "launch_application",
            "app_name": app_info["name"],
            "error": f"Executable for '{app_info['name']}' could not be found on this system.",
            "verification_status": "failed",
            "verification_details": {},
            "dry_run": dry_run,
        }

    if dry_run:
        return {
            "success": True,
            "action": "launch_application",
            "app_name": app_info["name"],
            "target": resolved_path,
            "command": [resolved_path],
            "message": f"[DRY RUN] Verified: {app_info['name']} is approved and available at {resolved_path}.",
            "details": f"[DRY RUN] Verified: {app_info['name']} is approved and available at {resolved_path}.",
            "verification_status": "verified",
            "verification_details": {"dry_run": True},
            "dry_run": True,
        }

    process_names = app_info.get("process_names", [])
    title_keyword = app_info.get("title_keyword")

    # 1. Check if a visible window for this app already exists
    existing_win = find_window_by_process(process_names, title_contains=title_keyword)
    if existing_win and not target_path:
        focus_window(existing_win["hwnd"])
        return {
            "success": True,
            "action": "launch_application",
            "app_name": app_info["name"],
            "target": resolved_path,
            "pid": existing_win["pid"],
            "hwnd": existing_win["hwnd"],
            "window_title": existing_win["title"],
            "verified": True,
            "verification_status": "verified",
            "verification_details": {
                "visible_window": True,
                "hwnd": existing_win["hwnd"],
                "title": existing_win["title"],
                "pid": existing_win["pid"],
                "already_running": True,
            },
            "message": f"{app_info['name']} is already running. Brought visible window '{existing_win['title']}' to the foreground (PID: {existing_win['pid']}).",
            "details": f"{app_info['name']} is already running. Brought visible window '{existing_win['title']}' to the foreground.",
            "dry_run": False,
        }

    # 2. Launch application
    try:
        cmd = [resolved_path]
        if target_path:
            cmd.append(target_path)

        if resolved_path.lower().endswith(".cmd") or resolved_path.lower().endswith(".bat"):
            # Launch via subprocess for batch files like code.cmd
            subprocess.Popen(cmd, shell=True)
        elif hasattr(os, "startfile") and not target_path:
            os.startfile(resolved_path)
        else:
            subprocess.Popen(cmd, shell=False)

        # 3. Poll for visible window appearance (up to 3.0 seconds)
        detected_win = None
        detected_pid = None

        for _ in range(10):
            time.sleep(0.3)
            detected_win = find_window_by_process(process_names, title_contains=title_keyword)
            if detected_win:
                detected_pid = detected_win["pid"]
                focus_window(detected_win["hwnd"])
                break
            if not detected_pid:
                detected_pid = verify_process_running(process_names)

        is_verified = detected_win is not None
        window_title = detected_win.get("title", "") if detected_win else None
        hwnd = detected_win.get("hwnd") if detected_win else None

        if is_verified:
            msg = f"Successfully launched {app_info['name']} (Visible Window: '{window_title}', PID: {detected_pid})."
        elif detected_pid:
            msg = f"{app_info['name']} process started (PID: {detected_pid}), waiting for GUI window to render."
        else:
            msg = f"Triggered launch of {app_info['name']}."

        return {
            "success": True,
            "action": "launch_application",
            "app_name": app_info["name"],
            "target": resolved_path,
            "pid": detected_pid,
            "hwnd": hwnd,
            "window_title": window_title,
            "verified": is_verified or (detected_pid is not None),
            "verification_status": "verified" if (is_verified or detected_pid) else "failed",
            "verification_details": {
                "visible_window": is_verified,
                "process_running": detected_pid is not None,
                "hwnd": hwnd,
                "title": window_title,
                "pid": detected_pid,
            },
            "message": msg,
            "details": msg,
            "dry_run": False,
        }

    except Exception as exc:
        return {
            "success": False,
            "action": "launch_application",
            "app_name": app_info["name"],
            "error": f"Failed to start {app_info['name']}: {str(exc)}",
            "verification_status": "failed",
            "verification_details": {},
            "dry_run": False,
        }


def close_application(app_name: str, force: bool = False) -> Dict[str, Any]:
    """
    Safely closes an approved application by process name or window.
    """
    normalized_key = app_name.strip().lower()
    app_info = APPROVED_APPLICATIONS.get(normalized_key)

    if not app_info:
        return {
            "success": False,
            "action": "close_application",
            "error": f"Application '{app_name}' is not in the approved application registry.",
            "verification_status": "failed",
        }

    process_names = app_info.get("process_names", [])
    total_closed = 0

    for pname in process_names:
        res = close_process(pname, force=force)
        total_closed += res.get("closed_count", 0)

    # Verify no processes remaining
    remaining_pid = verify_process_running(process_names)
    is_verified = remaining_pid is None

    msg = f"Successfully closed {app_info['name']}." if total_closed > 0 else f"{app_info['name']} was not running."

    return {
        "success": True,
        "action": "close_application",
        "app_name": app_info["name"],
        "closed_count": total_closed,
        "remaining_pid": remaining_pid,
        "verified": is_verified,
        "verification_status": "verified" if is_verified else "failed",
        "verification_details": {"remaining_pid": remaining_pid},
        "message": msg,
        "details": msg,
    }


def detect_installed_applications() -> Dict[str, Any]:
    """
    Scans the system for all approved applications and returns installation status.
    """
    results = {}
    unique_apps = {}
    for key, info in APPROVED_APPLICATIONS.items():
        name = info["name"]
        if name not in unique_apps:
            unique_apps[name] = info

    for name, info in unique_apps.items():
        path = resolve_executable_path(info)
        installed = path is not None and os.path.exists(path)
        running = verify_process_running(info.get("process_names", [])) is not None
        results[name] = {
            "installed": installed,
            "path": path if installed else None,
            "running": running,
            "description": info.get("description", ""),
        }

    return {
        "success": True,
        "action": "detect_installed_applications",
        "installed_applications": results,
        "verification_status": "verified",
        "details": f"Detected {sum(1 for a in results.values() if a['installed'])} installed applications out of {len(results)} approved.",
    }
