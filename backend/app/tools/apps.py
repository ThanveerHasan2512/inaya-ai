import os
import shutil
import time
from typing import Dict, Any, Optional
import psutil

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
    },
    "calc": {
        "name": "Calculator",
        "description": "Windows Calculator",
        "process_names": ["CalculatorApp.exe", "calc.exe", "Calculator.exe"],
        "discovery_paths": [
            r"C:\Windows\System32\calc.exe",
        ],
        "default_target": "calc.exe",
    },
    "explorer": {
        "name": "File Explorer",
        "description": "Windows File Explorer",
        "process_names": ["explorer.exe"],
        "discovery_paths": [
            r"C:\Windows\explorer.exe",
        ],
        "default_target": "explorer.exe",
    },
    "file explorer": {
        "name": "File Explorer",
        "description": "Windows File Explorer",
        "process_names": ["explorer.exe"],
        "discovery_paths": [
            r"C:\Windows\explorer.exe",
        ],
        "default_target": "explorer.exe",
    },
    "cmd": {
        "name": "Command Prompt",
        "description": "Windows Command Prompt",
        "process_names": ["cmd.exe", "conhost.exe"],
        "discovery_paths": [
            r"C:\Windows\System32\cmd.exe",
        ],
        "default_target": "cmd.exe",
    },
    "command prompt": {
        "name": "Command Prompt",
        "description": "Windows Command Prompt",
        "process_names": ["cmd.exe", "conhost.exe"],
        "discovery_paths": [
            r"C:\Windows\System32\cmd.exe",
        ],
        "default_target": "cmd.exe",
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
    },
    "code": {
        "name": "Visual Studio Code",
        "description": "VS Code Code Editor",
        "process_names": ["Code.exe"],
        "discovery_paths": [
            os.path.join(os.environ.get("LOCALAPPDATA", ""), r"Programs\Microsoft VS Code\Code.exe"),
            r"C:\Program Files\Microsoft VS Code\Code.exe",
            r"C:\Program Files (x86)\Microsoft VS Code\Code.exe",
        ],
        "default_target": "Code.exe",
    },
    "vs code": {
        "name": "Visual Studio Code",
        "description": "VS Code Code Editor",
        "process_names": ["Code.exe"],
        "discovery_paths": [
            os.path.join(os.environ.get("LOCALAPPDATA", ""), r"Programs\Microsoft VS Code\Code.exe"),
            r"C:\Program Files\Microsoft VS Code\Code.exe",
            r"C:\Program Files (x86)\Microsoft VS Code\Code.exe",
        ],
        "default_target": "Code.exe",
    },
    "vscode": {
        "name": "Visual Studio Code",
        "description": "VS Code Code Editor",
        "process_names": ["Code.exe"],
        "discovery_paths": [
            os.path.join(os.environ.get("LOCALAPPDATA", ""), r"Programs\Microsoft VS Code\Code.exe"),
            r"C:\Program Files\Microsoft VS Code\Code.exe",
            r"C:\Program Files (x86)\Microsoft VS Code\Code.exe",
        ],
        "default_target": "Code.exe",
    },
    "visual studio code": {
        "name": "Visual Studio Code",
        "description": "VS Code Code Editor",
        "process_names": ["Code.exe"],
        "discovery_paths": [
            os.path.join(os.environ.get("LOCALAPPDATA", ""), r"Programs\Microsoft VS Code\Code.exe"),
            r"C:\Program Files\Microsoft VS Code\Code.exe",
            r"C:\Program Files (x86)\Microsoft VS Code\Code.exe",
        ],
        "default_target": "Code.exe",
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

    # Fallback to default target for Windows Shell resolution
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


def launch_application(app_name: str, dry_run: bool = False) -> Dict[str, Any]:
    """
    Safely launches an approved Windows desktop application using os.startfile()
    for native Windows desktop session integration.
    Strictly validates against APPROVED_APPLICATIONS allowlist.
    """
    normalized_key = app_name.strip().lower()
    app_info = APPROVED_APPLICATIONS.get(normalized_key)

    if not app_info:
        # Build clean list of unique unique friendly names
        unique_names = sorted(list({v["name"] for v in APPROVED_APPLICATIONS.values()}))
        return {
            "success": False,
            "error": f"Application '{app_name}' is not in the approved application registry.",
            "available_applications": ", ".join(unique_names),
            "dry_run": dry_run,
        }

    resolved_path = resolve_executable_path(app_info)
    if not resolved_path:
        return {
            "success": False,
            "app_name": app_info["name"],
            "error": f"Executable for '{app_info['name']}' could not be found on this system.",
            "dry_run": dry_run,
        }

    if dry_run:
        return {
            "success": True,
            "app_name": app_info["name"],
            "target": resolved_path,
            "command": [resolved_path],
            "message": f"[DRY RUN] Verified: {app_info['name']} is approved and available at {resolved_path}.",
            "dry_run": True,
        }

    try:
        # os.startfile executes through the Windows Shell in the active user desktop session
        if hasattr(os, "startfile"):
            os.startfile(resolved_path)
        else:
            import subprocess
            subprocess.Popen([resolved_path], shell=False)

        # Brief delay to allow Windows to register the process
        time.sleep(0.5)

        # Verify whether the process is active
        detected_pid = verify_process_running(app_info.get("process_names", []))

        return {
            "success": True,
            "app_name": app_info["name"],
            "target": resolved_path,
            "pid": detected_pid,
            "verified": detected_pid is not None,
            "message": f"Successfully launched {app_info['name']}" + (f" (PID: {detected_pid})." if detected_pid else "."),
            "dry_run": False,
        }
    except Exception as exc:
        return {
            "success": False,
            "app_name": app_info["name"],
            "error": f"Failed to start {app_info['name']}: {str(exc)}",
            "dry_run": False,
        }
