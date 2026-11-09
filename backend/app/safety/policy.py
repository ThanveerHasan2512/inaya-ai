import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, Any, Tuple, Optional


class ActionSeverity(str, Enum):
    SAFE_READ_ONLY = "safe_read_only"
    LOW_RISK = "low_risk"
    WORKSPACE_MODIFICATION = "workspace_modification"
    SENSITIVE = "sensitive"
    DESTRUCTIVE = "destructive"


# Tool severity mapping
TOOL_SEVERITY_MAP = {
    "get_system_telemetry": ActionSeverity.SAFE_READ_ONLY,
    "get_system_info": ActionSeverity.SAFE_READ_ONLY,
    "get_running_processes": ActionSeverity.SAFE_READ_ONLY,
    "read_file": ActionSeverity.SAFE_READ_ONLY,
    "list_folder": ActionSeverity.SAFE_READ_ONLY,
    "search_files": ActionSeverity.SAFE_READ_ONLY,
    "detect_installed_applications": ActionSeverity.SAFE_READ_ONLY,
    "launch_application": ActionSeverity.LOW_RISK,
    "open_path": ActionSeverity.LOW_RISK,
    "open_website": ActionSeverity.LOW_RISK,
    "search_web": ActionSeverity.LOW_RISK,
    "create_file": ActionSeverity.WORKSPACE_MODIFICATION,
    "write_file": ActionSeverity.WORKSPACE_MODIFICATION,
    "create_folder": ActionSeverity.WORKSPACE_MODIFICATION,
    "create_python_project": ActionSeverity.WORKSPACE_MODIFICATION,
    "create_java_file": ActionSeverity.WORKSPACE_MODIFICATION,
    "run_program": ActionSeverity.SENSITIVE,
    "close_application": ActionSeverity.SENSITIVE,
    "rename_file": ActionSeverity.SENSITIVE,
    "copy_file": ActionSeverity.SENSITIVE,
    "move_file": ActionSeverity.SENSITIVE,
    "delete_file": ActionSeverity.DESTRUCTIVE,
    "delete_folder": ActionSeverity.DESTRUCTIVE,
}

# Pending approvals store in memory
_PENDING_APPROVALS: Dict[str, Dict[str, Any]] = {}


def evaluate_action_safety(tool_name: str, arguments: Dict[str, Any]) -> Tuple[bool, ActionSeverity, str]:
    """
    Evaluates whether an action requires explicit human confirmation.
    Returns: (requires_approval: bool, severity: ActionSeverity, explanation: str)
    """
    severity = TOOL_SEVERITY_MAP.get(tool_name, ActionSeverity.SENSITIVE)

    if severity == ActionSeverity.SAFE_READ_ONLY:
        return False, severity, "Safe read-only telemetry or inspection."

    if severity == ActionSeverity.LOW_RISK:
        return False, severity, f"Standard desktop execution: {tool_name}."

    if severity == ActionSeverity.WORKSPACE_MODIFICATION:
        # Check path location
        path = arguments.get("path") or arguments.get("directory") or ""
        if path.lower().startswith("d:\\") or "scratch" in path.lower() or "inaya" in path.lower():
            # Approved workspace modification
            return False, severity, "Non-destructive file operation inside approved workspace."
        return True, ActionSeverity.SENSITIVE, f"Operation modifies files outside standard project workspace: '{path}'."

    if severity == ActionSeverity.SENSITIVE:
        return True, severity, f"Sensitive action requires confirmation: {tool_name} with args {arguments}."

    if severity == ActionSeverity.DESTRUCTIVE:
        return True, severity, f"DESTRUCTIVE ACTION: {tool_name} will permanently remove or modify data."

    return False, ActionSeverity.LOW_RISK, "Default execution."


def create_approval_request(tool_name: str, arguments: Dict[str, Any], reason: str) -> Dict[str, Any]:
    """
    Registers a pending human approval request.
    """
    req_id = f"appr-{uuid.uuid4().hex[:8]}"
    record = {
        "id": req_id,
        "tool_name": tool_name,
        "arguments": arguments,
        "reason": reason,
        "status": "pending",
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    _PENDING_APPROVALS[req_id] = record
    return record


def approve_request(req_id: str) -> Optional[Dict[str, Any]]:
    if req_id in _PENDING_APPROVALS:
        _PENDING_APPROVALS[req_id]["status"] = "approved"
        return _PENDING_APPROVALS[req_id]
    return None


def reject_request(req_id: str) -> Optional[Dict[str, Any]]:
    if req_id in _PENDING_APPROVALS:
        _PENDING_APPROVALS[req_id]["status"] = "rejected"
        return _PENDING_APPROVALS[req_id]
    return None
