from typing import Dict, Any, List, Callable
from .apps import launch_application, APPROVED_APPLICATIONS
from .system import get_system_telemetry

TOOL_DEFINITIONS = [
    {
        "name": "launch_application",
        "description": "Safely launch an approved Windows desktop application (Notepad, Calculator, File Explorer, Command Prompt, Chrome, Edge, VS Code).",
        "parameters": {
            "type": "object",
            "properties": {
                "app_name": {
                    "type": "string",
                    "description": "Name of the application to launch (e.g. 'notepad', 'calculator', 'explorer').",
                    "enum": list(APPROVED_APPLICATIONS.keys()),
                },
                "dry_run": {
                    "type": "boolean",
                    "description": "If true, simulates launch without actually spawning the process.",
                    "default": False,
                },
            },
            "required": ["app_name"],
        },
    },
    {
        "name": "get_system_telemetry",
        "description": "Retrieve live CPU usage, RAM usage, D: drive free space, and system uptime.",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
]


def execute_tool(name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    """
    Executes a validated tool by name with arguments.
    """
    if name == "launch_application":
        app_name = arguments.get("app_name", "")
        dry_run = arguments.get("dry_run", False)
        return launch_application(app_name, dry_run=dry_run)

    elif name == "get_system_telemetry":
        return get_system_telemetry()

    return {
        "success": False,
        "error": f"Tool '{name}' is not registered in INAYA tool registry.",
    }
