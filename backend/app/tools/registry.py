from typing import Dict, Any, List

from .apps import launch_application, close_application, detect_installed_applications, APPROVED_APPLICATIONS
from ..system.system_tools import get_system_telemetry, get_system_info, get_running_processes
from ..files.file_tools import (
    create_file, read_file, write_file, create_folder,
    list_folder, search_files, rename_file, copy_file, move_file, open_path
)
from ..browser.browser_tools import open_website, search_web
from ..coding.coding_tools import create_python_project, create_java_file, run_program

TOOL_DEFINITIONS = [
    {
        "name": "launch_application",
        "description": "Safely launch an approved Windows desktop application (Notepad, Calculator, File Explorer, Command Prompt, Chrome, Edge, VS Code). Brings existing visible windows to the front.",
        "parameters": {
            "type": "object",
            "properties": {
                "app_name": {
                    "type": "string",
                    "description": "Name of the application to launch (e.g. 'notepad', 'calculator', 'explorer', 'code').",
                    "enum": list(APPROVED_APPLICATIONS.keys()),
                },
                "dry_run": {
                    "type": "boolean",
                    "description": "If true, simulates launch without actually spawning the process.",
                    "default": False,
                },
                "target_path": {
                    "type": "string",
                    "description": "Optional file or folder path to open with the application.",
                },
            },
            "required": ["app_name"],
        },
    },
    {
        "name": "close_application",
        "description": "Safely close an approved application (Notepad, Calculator, Chrome, VS Code, etc.).",
        "parameters": {
            "type": "object",
            "properties": {
                "app_name": {
                    "type": "string",
                    "description": "Name of the application to close.",
                    "enum": list(APPROVED_APPLICATIONS.keys()),
                },
                "force": {
                    "type": "boolean",
                    "description": "Force terminate the process if it does not close gracefully.",
                    "default": False,
                },
            },
            "required": ["app_name"],
        },
    },
    {
        "name": "detect_installed_applications",
        "description": "Scans Windows system for all approved applications and returns their installation and running status.",
        "parameters": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "get_system_telemetry",
        "description": "Retrieve live CPU usage, RAM usage, D: drive free space, system uptime, and battery status.",
        "parameters": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "get_system_info",
        "description": "Retrieve hardware and OS information (Windows release, machine architecture, RAM, CPU).",
        "parameters": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "get_running_processes",
        "description": "Lists top running desktop processes by memory utilization.",
        "parameters": {
            "type": "object",
            "properties": {
                "limit": {"type": "integer", "description": "Maximum number of processes to return (default: 15).", "default": 15}
            },
            "required": [],
        },
    },
    {
        "name": "create_file",
        "description": "Create a new text or code file with given content in an approved workspace.",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Absolute or relative file path to create."},
                "content": {"type": "string", "description": "Text content to write to the file.", "default": ""},
            },
            "required": ["path"],
        },
    },
    {
        "name": "read_file",
        "description": "Read text content from a file in an approved workspace.",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "File path to read."},
                "max_bytes": {"type": "integer", "description": "Max bytes to read (default: 100,000).", "default": 100000},
            },
            "required": ["path"],
        },
    },
    {
        "name": "write_file",
        "description": "Write or append text content to an existing file in an approved workspace.",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "File path to write to."},
                "content": {"type": "string", "description": "Text content to write."},
                "append": {"type": "boolean", "description": "Whether to append to the end of the file.", "default": False},
            },
            "required": ["path", "content"],
        },
    },
    {
        "name": "create_folder",
        "description": "Create a new folder/directory inside an approved workspace.",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Folder directory path to create."},
            },
            "required": ["path"],
        },
    },
    {
        "name": "list_folder",
        "description": "List files and subdirectories inside a folder.",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Folder path to list."},
            },
            "required": ["path"],
        },
    },
    {
        "name": "search_files",
        "description": "Search for files matching a wildcard pattern (e.g. '*.py', 'notes*') inside a directory.",
        "parameters": {
            "type": "object",
            "properties": {
                "directory": {"type": "string", "description": "Root directory to search inside."},
                "query": {"type": "string", "description": "Wildcard search pattern (e.g. '*.txt').", "default": "*"},
                "recursive": {"type": "boolean", "description": "Whether to search subdirectories.", "default": True},
            },
            "required": ["directory"],
        },
    },
    {
        "name": "rename_file",
        "description": "Rename a file or folder.",
        "parameters": {
            "type": "object",
            "properties": {
                "old_path": {"type": "string", "description": "Current file path."},
                "new_path": {"type": "string", "description": "New file path."},
            },
            "required": ["old_path", "new_path"],
        },
    },
    {
        "name": "copy_file",
        "description": "Copy a file or directory to a new destination.",
        "parameters": {
            "type": "object",
            "properties": {
                "source_path": {"type": "string", "description": "Source file path."},
                "destination_path": {"type": "string", "description": "Target destination path."},
            },
            "required": ["source_path", "destination_path"],
        },
    },
    {
        "name": "move_file",
        "description": "Move a file or directory to a new destination.",
        "parameters": {
            "type": "object",
            "properties": {
                "source_path": {"type": "string", "description": "Source file path."},
                "destination_path": {"type": "string", "description": "Target destination path."},
            },
            "required": ["source_path", "destination_path"],
        },
    },
    {
        "name": "open_path",
        "description": "Open a file or folder natively in Windows (File Explorer or associated app).",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "File or folder path to open in Windows."},
            },
            "required": ["path"],
        },
    },
    {
        "name": "open_website",
        "description": "Open a website in the default web browser.",
        "parameters": {
            "type": "object",
            "properties": {
                "url": {"type": "string", "description": "Web URL to open (e.g. 'https://github.com')."},
            },
            "required": ["url"],
        },
    },
    {
        "name": "search_web",
        "description": "Search the web for a topic or question in the browser.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search query text."},
            },
            "required": ["query"],
        },
    },
    {
        "name": "create_python_project",
        "description": "Scaffold a clean Python project with main.py, requirements.txt, and README.md.",
        "parameters": {
            "type": "object",
            "properties": {
                "project_name": {"type": "string", "description": "Project directory name."},
                "directory": {"type": "string", "description": "Parent directory (default: D:\\INAYA\\scratch)."},
            },
            "required": ["project_name"],
        },
    },
    {
        "name": "create_java_file",
        "description": "Create a clean Java source file with a main class.",
        "parameters": {
            "type": "object",
            "properties": {
                "class_name": {"type": "string", "description": "Java class name (e.g. 'Main')."},
                "directory": {"type": "string", "description": "Parent directory (default: D:\\INAYA\\scratch)."},
                "package_name": {"type": "string", "description": "Optional package declaration."},
            },
            "required": ["class_name"],
        },
    },
    {
        "name": "run_program",
        "description": "Safely execute a Python script inside the project environment and capture its output and errors.",
        "parameters": {
            "type": "object",
            "properties": {
                "script_path": {"type": "string", "description": "Path to the Python script to execute."},
                "timeout": {"type": "integer", "description": "Timeout in seconds (default: 15).", "default": 15},
            },
            "required": ["script_path"],
        },
    },
]


def execute_tool(name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    """
    Executes a validated tool by name with arguments.
    Always returns structured, verified execution details.
    """
    # 1. Application tools
    if name == "launch_application":
        app_name = arguments.get("app_name", "")
        dry_run = arguments.get("dry_run", False)
        target_path = arguments.get("target_path")
        return launch_application(app_name, dry_run=dry_run, target_path=target_path)

    elif name == "close_application":
        app_name = arguments.get("app_name", "")
        force = arguments.get("force", False)
        return close_application(app_name, force=force)

    elif name == "detect_installed_applications":
        return detect_installed_applications()

    # 2. System tools
    elif name == "get_system_telemetry":
        return get_system_telemetry()

    elif name == "get_system_info":
        return get_system_info()

    elif name == "get_running_processes":
        limit = arguments.get("limit", 15)
        return get_running_processes(limit=limit)

    # 3. File tools
    elif name == "create_file":
        return create_file(arguments.get("path", ""), arguments.get("content", ""))

    elif name == "read_file":
        return read_file(arguments.get("path", ""), arguments.get("max_bytes", 100000))

    elif name == "write_file":
        return write_file(arguments.get("path", ""), arguments.get("content", ""), arguments.get("append", False))

    elif name == "create_folder":
        return create_folder(arguments.get("path", ""))

    elif name == "list_folder":
        return list_folder(arguments.get("path", ""))

    elif name == "search_files":
        return search_files(arguments.get("directory", ""), arguments.get("query", "*"), arguments.get("recursive", True))

    elif name == "rename_file":
        return rename_file(arguments.get("old_path", ""), arguments.get("new_path", ""))

    elif name == "copy_file":
        return copy_file(arguments.get("source_path", ""), arguments.get("destination_path", ""))

    elif name == "move_file":
        return move_file(arguments.get("source_path", ""), arguments.get("destination_path", ""))

    elif name == "open_path":
        return open_path(arguments.get("path", ""))

    # 4. Browser tools
    elif name == "open_website":
        return open_website(arguments.get("url", ""))

    elif name == "search_web":
        return search_web(arguments.get("query", ""))

    # 5. Coding tools
    elif name == "create_python_project":
        return create_python_project(arguments.get("project_name", ""), arguments.get("directory"))

    elif name == "create_java_file":
        return create_java_file(arguments.get("class_name", ""), arguments.get("directory"), arguments.get("package_name"))

    elif name == "run_program":
        return run_program(arguments.get("script_path", ""), arguments.get("timeout", 15))

    return {
        "success": False,
        "action": name,
        "error": f"Tool '{name}' is not registered in INAYA tool registry.",
        "verification_status": "failed",
    }
