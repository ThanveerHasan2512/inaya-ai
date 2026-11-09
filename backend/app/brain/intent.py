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

# Patterns for conversational fluff to strip when extracting target
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
    Parses natural language input into structured intent and entities.
    Returns a dictionary with:
    - intent: 'LAUNCH_APP' | 'SYSTEM_TELEMETRY' | 'TIME_DATE' | 'GREETING' | 'HELP' | 'UNKNOWN'
    - tool: associated tool name if applicable
    - arguments: parameters for the tool
    - confidence: float score
    """
    raw = user_text.strip()
    if not raw:
        return {"intent": "EMPTY", "tool": None, "arguments": {}, "confidence": 0.0}

    # Normalize: lowercase, remove punctuation at borders
    clean = raw.lower()
    clean = re.sub(r"[?!.,;]+$", "", clean).strip()

    # Strip leading conversational fluff
    normalized = clean
    for pat in CONVERSATIONAL_PREFIXES:
        normalized = re.sub(pat, "", normalized).strip()

    # 1. Check for Greetings
    if re.search(r"\b(hello|hi|hey|good\s+(morning|afternoon|evening)|greetings)\b", clean):
        # Only treat as pure greeting if it's not also asking to do an action
        has_action = any(v in clean for v in LAUNCH_VERBS) or any(k in clean for k in ["cpu", "ram", "status", "time"])
        if not has_action or len(clean.split()) <= 4:
            return {"intent": "GREETING", "tool": None, "arguments": {}, "confidence": 0.95}

    # 2. Check for Help / Capabilities
    if re.search(r"\b(help|what can you do|capabilities|list commands|show commands|what apps|which apps)\b", clean):
        return {"intent": "HELP", "tool": None, "arguments": {}, "confidence": 0.9}

    # 3. Check for System Telemetry
    if re.search(r"\b(system\s*(stats|status|telemetry|health|vitals)|cpu|ram|memory\s*usage|disk\s*space|storage|uptime|what is happening on my (computer|pc))\b", clean):
        return {
            "intent": "SYSTEM_TELEMETRY",
            "tool": "get_system_telemetry",
            "arguments": {},
            "confidence": 0.95,
        }

    # 4. Check for Time / Date
    if re.search(r"\b(what time is it|current time|tell me the time|time now|today'?s date|current date|what day is it)\b", clean):
        return {"intent": "TIME_DATE", "tool": None, "arguments": {}, "confidence": 0.95}

    # 5. Check for Application Launching
    # Check if a launch verb is present
    has_launch_verb = any(v in clean for v in LAUNCH_VERBS)

    # Search for known app entities in order of key length descending (to match "visual studio code" before "code")
    sorted_entities = sorted(APP_ENTITY_MAP.keys(), key=len, reverse=True)
    for entity in sorted_entities:
        # Match entity as a distinct word/phrase
        pattern = r"\b" + re.escape(entity) + r"\b"
        if re.search(pattern, clean):
            canonical_app = APP_ENTITY_MAP[entity]
            return {
                "intent": "LAUNCH_APP",
                "tool": "launch_application",
                "arguments": {"app_name": canonical_app},
                "confidence": 0.95 if has_launch_verb else 0.85,
            }

    # If launch verb is present but no known app matched, check if an unapproved app was requested
    if has_launch_verb:
        # Extract the target word after the launch verb
        for verb in LAUNCH_VERBS:
            match = re.search(rf"\b{verb}\s+(the\s+|my\s+|an\s+)?([a-zA-Z0-9_\-\.]+)", clean)
            if match:
                candidate = match.group(2).strip()
                if candidate not in ["up", "for", "please", "now", "it"]:
                    return {
                        "intent": "LAUNCH_UNAPPROVED_APP",
                        "tool": None,
                        "arguments": {"app_name": candidate},
                        "confidence": 0.7,
                    }

    return {"intent": "UNKNOWN", "tool": None, "arguments": {}, "confidence": 0.0}
