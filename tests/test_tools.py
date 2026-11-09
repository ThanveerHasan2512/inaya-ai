from app.tools.apps import launch_application, APPROVED_APPLICATIONS
from app.tools.registry import execute_tool


def test_approved_applications_allowlist():
    assert "notepad" in APPROVED_APPLICATIONS
    assert "calculator" in APPROVED_APPLICATIONS
    assert "calc" in APPROVED_APPLICATIONS
    assert "explorer" in APPROVED_APPLICATIONS


def test_launch_application_dry_run():
    result = launch_application("notepad", dry_run=True)
    assert result["success"] is True
    assert result["dry_run"] is True
    assert "notepad" in result["command"][0].lower()


def test_launch_application_unapproved_blocked():
    result = launch_application("malicious_script.bat", dry_run=True)
    assert result["success"] is False
    assert "not in the approved application registry" in result["error"]


def test_execute_tool_registry():
    res = execute_tool("launch_application", {"app_name": "calc", "dry_run": True})
    assert res["success"] is True
    assert res["dry_run"] is True
