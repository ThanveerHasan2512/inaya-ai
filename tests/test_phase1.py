import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.brain.intent import extract_intent
from app.tools.apps import launch_application, APPROVED_APPLICATIONS


def test_intent_natural_language_variations():
    # 1. Notepad variations
    cases_notepad = [
        "Open Notepad",
        "Can you launch Notepad?",
        "I want to use Notepad",
        "Please open my text editor",
        "Start notepad please",
        "bring up notes",
    ]
    for phrase in cases_notepad:
        res = extract_intent(phrase)
        assert res["intent"] == "LAUNCH_APP", f"Failed for phrase: {phrase}"
        assert res["arguments"]["app_name"] == "notepad", f"Wrong app for: {phrase}"

    # 2. Calculator variations
    cases_calc = [
        "Open Calculator",
        "Launch the calculator",
        "Could you please start calc?",
        "I need calculator",
    ]
    for phrase in cases_calc:
        res = extract_intent(phrase)
        assert res["intent"] == "LAUNCH_APP", f"Failed for phrase: {phrase}"
        assert res["arguments"]["app_name"] == "calculator", f"Wrong app for: {phrase}"

    # 3. File Explorer variations
    cases_explorer = [
        "Open File Explorer",
        "Bring up explorer",
        "Can you show my files?",
        "Launch file manager",
    ]
    for phrase in cases_explorer:
        res = extract_intent(phrase)
        assert res["intent"] == "LAUNCH_APP", f"Failed for phrase: {phrase}"
        assert res["arguments"]["app_name"] == "explorer", f"Wrong app for: {phrase}"

    # 4. VS Code variations
    cases_vscode = [
        "Open VS Code",
        "Launch Visual Studio Code",
        "Start code editor",
        "Can you open vscode?",
    ]
    for phrase in cases_vscode:
        res = extract_intent(phrase)
        assert res["intent"] == "LAUNCH_APP", f"Failed for phrase: {phrase}"
        assert res["arguments"]["app_name"] == "code", f"Wrong app for: {phrase}"

    # 5. Browsers (Chrome & Edge)
    assert extract_intent("Open Google Chrome")["arguments"]["app_name"] == "chrome"
    assert extract_intent("Launch Microsoft Edge")["arguments"]["app_name"] == "edge"

    # 6. Command Prompt
    assert extract_intent("Open Command Prompt")["arguments"]["app_name"] == "cmd"
    assert extract_intent("Start terminal")["arguments"]["app_name"] == "cmd"


def test_intent_telemetry_and_clock():
    res_sys = extract_intent("What is happening on my computer?")
    assert res_sys["intent"] == "SYSTEM_TELEMETRY"

    res_vitals = extract_intent("Check CPU and RAM usage")
    assert res_vitals["intent"] == "SYSTEM_TELEMETRY"

    res_time = extract_intent("What time is it right now?")
    assert res_time["intent"] == "TIME_DATE"


def test_unapproved_application_blocked():
    res = extract_intent("Launch arbitrary_virus.exe")
    assert res["intent"] == "LAUNCH_UNAPPROVED_APP"
    assert res["arguments"]["app_name"] == "arbitrary_virus.exe"


def test_application_allowlist_and_dry_run():
    # Verify all approved apps support dry_run
    approved_keys = ["notepad", "calculator", "explorer", "cmd", "chrome", "edge", "code"]
    for key in approved_keys:
        res = launch_application(key, dry_run=True)
        assert res["success"] is True, f"Dry run failed for {key}: {res.get('error')}"
        assert res["dry_run"] is True

    # Verify unapproved executable is strictly rejected
    bad_res = launch_application("malicious_tool.bat", dry_run=True)
    assert bad_res["success"] is False
    assert "not in the approved application registry" in bad_res["error"]


@pytest.mark.asyncio
async def test_chat_pipeline_nlp_execution():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Natural phrasing: "Can you please open Notepad?"
        res1 = await client.post("/api/chat", json={"message": "Can you please open Notepad?"})
        assert res1.status_code == 200
        data1 = res1.json()
        assert len(data1["tools_executed"]) == 1
        assert data1["tools_executed"][0]["tool"] == "launch_application"
        assert data1["tools_executed"][0]["args"]["app_name"] == "notepad"
        assert "Notepad" in data1["reply"]

        # 2. Natural phrasing: "I want to use calculator"
        res2 = await client.post("/api/chat", json={"message": "I want to use calculator"})
        assert res2.status_code == 200
        data2 = res2.json()
        assert len(data2["tools_executed"]) == 1
        assert data2["tools_executed"][0]["tool"] == "launch_application"
        assert data2["tools_executed"][0]["args"]["app_name"] == "calculator"
        assert "Calculator" in data2["reply"]

        # 3. Security test: "Open unknown_game.exe"
        res3 = await client.post("/api/chat", json={"message": "Open unknown_game.exe"})
        assert res3.status_code == 200
        data3 = res3.json()
        assert len(data3["tools_executed"]) == 0
        assert "not in the allowlist" in data3["reply"]
