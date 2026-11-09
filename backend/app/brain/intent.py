import re
from typing import Dict, Any, Optional

# Synonyms and mapping for approved applications
APP_ENTITY_MAP = {
    # Notepad
    "notepad": "notepad",
    "notes": "notepad",
    "text editor": "notepad",
    "texteditor": "notepad",
    "notepad.exe": "notepad",
    # Calculator
    "calculator": "calculator",
    "calc": "calculator",
    "math tool": "calculator",
    "calc.exe": "calculator",
    # File Explorer
    "file explorer": "explorer",
    "explorer": "explorer",
    "file manager": "explorer",
    "files": "explorer",
    "file browser": "explorer",
    "my files": "explorer",
    "explorer.exe": "explorer",
    # Command Prompt
    "cmd": "cmd",
    "command prompt": "cmd",
    "terminal": "cmd",
    "console": "cmd",
    "cmd.exe": "cmd",
    # Google Chrome
    "chrome": "chrome",
    "google chrome": "chrome",
    "chrome browser": "chrome",
    # Microsoft Edge
    "edge": "edge",
    "microsoft edge": "edge",
    "ms edge": "edge",
    "edge browser": "edge",
    # Visual Studio Code
    "vs code": "code",
    "vscode": "code",
    "code": "code",
    "visual studio code": "code",
    "code editor": "code",
}

# Verbs that indicate launching/opening
LAUNCH_VERBS = [
    "open",
    "launch",
    "start",
    "run",
    "bring up",
    "show",
    "access",
    "load",
    "use",
    "fire up",
]

# Verbs that indicate closing/quitting
CLOSE_VERBS = [
    "close",
    "exit",
    "quit",
    "terminate",
    "kill",
    "stop",
    "shut down",
]

CONVERSATIONAL_PREFIXES = [
    r"^can you please\s+",
    r"^could you please\s+",
    r"^please\s+",
    r"^can you\s+",
    r"^could you\s+",
    r"^would you\s+",
    r"^i want to\s+",
    r"^i need to\s+",
    r"^i'd like to\s+",
    r"^help me\s+",
    r"^go ahead and\s+",
    r"^just\s+",
]


def extract_intent(user_text: str) -> Dict[str, Any]:
    """
    Parses natural language input into structured intent, tool name, and arguments.
    """
    raw = user_text.strip()
    if not raw:
        return {"intent": "EMPTY", "tool": None, "arguments": {}, "confidence": 0.0}

    clean = raw.lower()
    clean = re.sub(r"[?!.,;]+$", "", clean).strip()

    normalized = clean
    for pat in CONVERSATIONAL_PREFIXES:
        normalized = re.sub(pat, "", normalized).strip()

    # 1. Greetings
    if re.search(r"\b(hello|hi|hey|good\s+(morning|afternoon|evening)|greetings)\b", clean):
        has_action = any(v in clean for v in LAUNCH_VERBS + CLOSE_VERBS) or any(k in clean for k in ["cpu", "ram", "status", "time", "file", "folder"])
        if not has_action or len(clean.split()) <= 4:
            return {"intent": "GREETING", "tool": None, "arguments": {}, "confidence": 0.95}

    # 2. Help / Capabilities
    if re.search(r"\b(help|what can you do|capabilities|list commands|show commands|what apps|which apps)\b", clean):
        return {"intent": "HELP", "tool": None, "arguments": {}, "confidence": 0.9}

    # 3. Detect Installed Applications
    if re.search(r"\b(detect installed apps|detect installed applications|list installed apps|what apps are installed)\b", clean):
        return {
            "intent": "DETECT_APPS",
            "tool": "detect_installed_applications",
            "arguments": {},
            "confidence": 0.95,
        }

    # 4. Closing Applications
    has_close_verb = any(v in clean for v in CLOSE_VERBS)
    if has_close_verb:
        sorted_entities = sorted(APP_ENTITY_MAP.keys(), key=len, reverse=True)
        for entity in sorted_entities:
            pattern = r"\b" + re.escape(entity) + r"\b"
            if re.search(pattern, clean):
                canonical_app = APP_ENTITY_MAP[entity]
                return {
                    "intent": "CLOSE_APP",
                    "tool": "close_application",
                    "arguments": {"app_name": canonical_app},
                    "confidence": 0.95,
                }

    # 5. File Explorer with Specific Path (e.g. "Open File Explorer at D:\INAYA")
    if "explorer" in clean or "files" in clean:
        path_match = re.search(r"(?:at|in|to)\s+([a-zA-Z]:\\[^\s]+|[a-zA-Z]:/[^\s]+)", raw, re.IGNORECASE)
        if path_match:
            target = path_match.group(1).strip()
            return {
                "intent": "OPEN_PATH",
                "tool": "open_path",
                "arguments": {"path": target},
                "confidence": 0.95,
            }

    # 6. File Tools
    # 6a. Create Folder
    folder_match = re.search(r"\b(?:create|make|new)\s+(?:folder|directory)\s+(?:at\s+|named\s+|called\s+)?([^\s,;]+)", raw, re.IGNORECASE)
    if folder_match:
        fpath = folder_match.group(1).strip().strip("'\"")
        return {
            "intent": "CREATE_FOLDER",
            "tool": "create_folder",
            "arguments": {"path": fpath},
            "confidence": 0.95,
        }

    # 6b. Create / Write File
    create_file_match = re.search(r"\bcreate\s+(?:a\s+)?(?:text\s+)?file\s+(?:at\s+|named\s+|called\s+)?([^\s,;]+)(?:\s+(?:with|containing)\s+(?:content\s+|text\s+)?(.+))?", raw, re.IGNORECASE)
    if create_file_match:
        filepath = create_file_match.group(1).strip().strip("'\"")
        content = create_file_match.group(2).strip().strip("'\"") if create_file_match.group(2) else ""
        return {
            "intent": "CREATE_FILE",
            "tool": "create_file",
            "arguments": {"path": filepath, "content": content},
            "confidence": 0.95,
        }

    write_match = re.search(r"\bwrite\s+(?:text\s+)?(?:['\"](.+?)['\"]|(.+?))\s+to\s+(?:file\s+)?([^\s,;]+)", raw, re.IGNORECASE)
    if write_match:
        content = (write_match.group(1) or write_match.group(2) or "").strip()
        filepath = write_match.group(3).strip().strip("'\"")
        return {
            "intent": "WRITE_FILE",
            "tool": "write_file",
            "arguments": {"path": filepath, "content": content},
            "confidence": 0.95,
        }

    # 6c. Read File
    read_match = re.search(r"\b(?:read|display|view|show\s+contents?\s+of)\s+(?:the\s+)?file\s+([^\s,;]+)", raw, re.IGNORECASE)
    if read_match:
        filepath = read_match.group(1).strip().strip("'\"")
        return {
            "intent": "READ_FILE",
            "tool": "read_file",
            "arguments": {"path": filepath},
            "confidence": 0.95,
        }

    # 6d. List Folder
    list_match = re.search(r"\b(?:list|show|browse)\s+(?:files\s+in\s+|folder\s+|directory\s+)?([a-zA-Z]:\\[^\s,;]+|[a-zA-Z]:/[^\s,;]+)", raw, re.IGNORECASE)
    if list_match:
        fpath = list_match.group(1).strip().strip("'\"")
        return {
            "intent": "LIST_FOLDER",
            "tool": "list_folder",
            "arguments": {"path": fpath},
            "confidence": 0.9,
        }

    # 7. System Tools
    # Running processes
    if re.search(r"\b(running\s*processes|top\s*processes|list\s*processes|process\s*list|what is using (cpu|ram|memory))\b", clean):
        return {
            "intent": "SYSTEM_PROCESSES",
            "tool": "get_running_processes",
            "arguments": {"limit": 10},
            "confidence": 0.95,
        }

    # System Info
    if re.search(r"\b(system\s*info|specs|computer\s*specs|os\s*info|machine\s*info|hardware\s*info)\b", clean):
        return {
            "intent": "SYSTEM_INFO",
            "tool": "get_system_info",
            "arguments": {},
            "confidence": 0.95,
        }

    # System Telemetry & Vitals
    if re.search(r"\b(system\s*(stats|status|telemetry|health|vitals)|cpu|ram|memory\s*usage|disk\s*space|storage|battery|uptime|what is happening on my (computer|pc))\b", clean):
        return {
            "intent": "SYSTEM_TELEMETRY",
            "tool": "get_system_telemetry",
            "arguments": {},
            "confidence": 0.95,
        }

    # Time & Date
    if re.search(r"\b(what time is it|current time|tell me the time|time now|today'?s date|current date|what day is it)\b", clean):
        return {"intent": "TIME_DATE", "tool": None, "arguments": {}, "confidence": 0.95}

    # 8. Browser Tools
    web_match = re.search(r"\b(?:open|go\s+to|navigate\s+to|browse\s+to)\s+(?:website\s+)?(https?://[^\s]+|www\.[^\s]+|[a-zA-Z0-9_\-]+\.(?:com|org|io|dev|net|edu))\b", raw, re.IGNORECASE)
    if web_match:
        url = web_match.group(1).strip()
        return {
            "intent": "OPEN_WEBSITE",
            "tool": "open_website",
            "arguments": {"url": url},
            "confidence": 0.95,
        }

    search_match = re.search(r"\b(?:search\s+the\s+web\s+for|search\s+google\s+for|search\s+for|google\s+(?!chrome|docs|drive))\s+(.+)", raw, re.IGNORECASE)
    if search_match:
        query = search_match.group(1).strip()
        return {
            "intent": "SEARCH_WEB",
            "tool": "search_web",
            "arguments": {"query": query},
            "confidence": 0.95,
        }

    # 9. Coding Tools
    py_proj_match = re.search(r"\bcreate\s+(?:a\s+)?python\s+project\s+(?:named\s+|called\s+)?([^\s,;]+)", raw, re.IGNORECASE)
    if py_proj_match:
        pname = py_proj_match.group(1).strip().strip("'\"")
        return {
            "intent": "CREATE_PYTHON_PROJECT",
            "tool": "create_python_project",
            "arguments": {"project_name": pname},
            "confidence": 0.95,
        }

    java_file_match = re.search(r"\bcreate\s+(?:a\s+)?java\s+(?:file|class)\s+(?:named\s+|called\s+)?([^\s,;]+)", raw, re.IGNORECASE)
    if java_file_match:
        cname = java_file_match.group(1).strip().strip("'\"")
        return {
            "intent": "CREATE_JAVA_FILE",
            "tool": "create_java_file",
            "arguments": {"class_name": cname},
            "confidence": 0.95,
        }

    # 10. Application Launching
    has_launch_verb = any(v in clean for v in LAUNCH_VERBS)
    sorted_entities = sorted(APP_ENTITY_MAP.keys(), key=len, reverse=True)
    for entity in sorted_entities:
        pattern = r"\b" + re.escape(entity) + r"\b"
        if re.search(pattern, clean):
            canonical_app = APP_ENTITY_MAP[entity]
            return {
                "intent": "LAUNCH_APP",
                "tool": "launch_application",
                "arguments": {"app_name": canonical_app},
                "confidence": 0.95 if has_launch_verb else 0.85,
            }

    # Unapproved application attempt
    if has_launch_verb:
        for verb in LAUNCH_VERBS:
            match = re.search(rf"\b{verb}\s+(the\s+|my\s+|an\s+)?([a-zA-Z0-9_\-\.]+)", clean)
            if match:
                candidate = match.group(2).strip()
                if candidate not in ["up", "for", "please", "now", "it", "website", "file", "folder", "project"]:
                    return {
                        "intent": "LAUNCH_UNAPPROVED_APP",
                        "tool": None,
                        "arguments": {"app_name": candidate},
                        "confidence": 0.7,
                    }

    return {"intent": "UNKNOWN", "tool": None, "arguments": {}, "confidence": 0.0}
