import os
import shutil
import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.tools.apps import launch_application, APPROVED_APPLICATIONS
from app.files.file_tools import create_file, is_path_safe
from app.brain.providers.ollama import OllamaProvider


TEST_WORKSPACE = r"D:\INAYA\scratch\mandatory_tests"


@pytest.fixture(scope="module", autouse=True)
def setup_teardown_workspace():
    os.makedirs(TEST_WORKSPACE, exist_ok=True)
    yield
    # Cleanup after tests
    if os.path.exists(TEST_WORKSPACE):
        try:
            shutil.rmtree(TEST_WORKSPACE, ignore_errors=True)
        except Exception:
            pass


@pytest.mark.asyncio
async def test_scenario_01_typed_open_notepad():
    """Scenario 1: Typed command - Open Notepad"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.post("/api/chat", json={"message": "Open Notepad"})
        assert res.status_code == 200
        data = res.json()
        assert len(data["tools_executed"]) == 1
        tool = data["tools_executed"][0]
        assert tool["tool"] == "launch_application"
        assert tool["result"]["success"] is True
        assert tool["result"]["verification_status"] == "verified"


@pytest.mark.asyncio
async def test_scenario_02_voice_open_notepad():
    """Scenario 2: Voice command - Open Notepad (speech transcript routed via command API)"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        voice_transcript = "Please open Notepad"
        res = await client.post("/api/chat", json={"message": voice_transcript})
        assert res.status_code == 200
        data = res.json()
        assert len(data["tools_executed"]) == 1
        assert data["tools_executed"][0]["result"]["success"] is True


@pytest.mark.asyncio
async def test_scenario_03_typed_open_vscode():
    """Scenario 3: Typed command - Open VS Code with visible window verification"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.post("/api/chat", json={"message": "Open VS Code"})
        assert res.status_code == 200
        data = res.json()
        assert len(data["tools_executed"]) == 1
        tool = data["tools_executed"][0]
        assert tool["tool"] == "launch_application"
        assert tool["result"]["success"] is True
        assert tool["result"]["verification_status"] == "verified"
        assert tool["result"]["app_name"] == "Visual Studio Code"


@pytest.mark.asyncio
async def test_scenario_04_voice_open_vscode():
    """Scenario 4: Voice command - Open VS Code"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        voice_transcript = "Launch Visual Studio Code"
        res = await client.post("/api/chat", json={"message": voice_transcript})
        assert res.status_code == 200
        data = res.json()
        assert len(data["tools_executed"]) == 1
        assert data["tools_executed"][0]["result"]["success"] is True


@pytest.mark.asyncio
async def test_scenario_05_create_folder_approved_workspace():
    """Scenario 5: Create a folder inside an approved workspace"""
    folder_path = os.path.join(TEST_WORKSPACE, "subfolder_alpha")
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.post("/api/chat", json={"message": f"Create folder {folder_path}"})
        assert res.status_code == 200
        data = res.json()
        assert len(data["tools_executed"]) == 1
        assert data["tools_executed"][0]["tool"] == "create_folder"
        assert data["tools_executed"][0]["result"]["success"] is True
        # Verify real Windows filesystem effect
        assert os.path.isdir(folder_path)


@pytest.mark.asyncio
async def test_scenario_06_create_text_file():
    """Scenario 6: Create a text file"""
    file_path = os.path.join(TEST_WORKSPACE, "sample.txt")
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.post("/api/chat", json={
            "message": f"Create file {file_path} with content Hello INAYA Real Windows Test"
        })
        assert res.status_code == 200
        data = res.json()
        assert len(data["tools_executed"]) == 1
        assert data["tools_executed"][0]["tool"] == "create_file"
        assert data["tools_executed"][0]["result"]["success"] is True
        # Verify real Windows filesystem effect
        assert os.path.isfile(file_path)


@pytest.mark.asyncio
async def test_scenario_07_write_text_to_file():
    """Scenario 7: Write text to the file"""
    file_path = os.path.join(TEST_WORKSPACE, "sample.txt")
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.post("/api/chat", json={
            "message": f"Write 'Updated text content from phase 9.' to file {file_path}"
        })
        assert res.status_code == 200
        data = res.json()
        assert len(data["tools_executed"]) == 1
        assert data["tools_executed"][0]["tool"] == "write_file"
        assert data["tools_executed"][0]["result"]["success"] is True
        # Verify content on disk
        with open(file_path, "r", encoding="utf-8") as f:
            disk_content = f.read()
        assert "Updated text content" in disk_content


@pytest.mark.asyncio
async def test_scenario_08_read_file():
    """Scenario 8: Read the file"""
    file_path = os.path.join(TEST_WORKSPACE, "sample.txt")
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.post("/api/chat", json={"message": f"Read file {file_path}"})
        assert res.status_code == 200
        data = res.json()
        assert len(data["tools_executed"]) == 1
        assert data["tools_executed"][0]["tool"] == "read_file"
        assert data["tools_executed"][0]["result"]["success"] is True
        assert "Updated text content" in data["tools_executed"][0]["result"]["content"]


@pytest.mark.asyncio
async def test_scenario_09_open_file_explorer_at_inaya():
    """Scenario 9: Open File Explorer at D:\\INAYA"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.post("/api/chat", json={"message": "Open File Explorer at D:\\INAYA"})
        assert res.status_code == 200
        data = res.json()
        assert len(data["tools_executed"]) == 1
        tool = data["tools_executed"][0]
        assert tool["tool"] == "open_path"
        assert tool["result"]["success"] is True
        assert "D:\\INAYA" in tool["result"]["path"]


@pytest.mark.asyncio
async def test_scenario_10_retrieve_system_ram_usage():
    """Scenario 10: Retrieve system RAM usage"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.post("/api/chat", json={"message": "Check RAM usage"})
        assert res.status_code == 200
        data = res.json()
        assert len(data["tools_executed"]) == 1
        tool = data["tools_executed"][0]
        assert tool["tool"] == "get_system_telemetry"
        assert tool["result"]["success"] is True
        ram = tool["result"]["ram_usage"]
        assert isinstance(ram, (int, float)) and ram > 0


@pytest.mark.asyncio
async def test_scenario_11_handle_unknown_commands():
    """Scenario 11: Handle unknown commands gracefully"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.post("/api/chat", json={"message": "xyzzy foobar blub 123456789"})
        assert res.status_code == 200
        data = res.json()
        assert len(data["tools_executed"]) == 0
        assert "I received" in data["reply"] or "How can I assist" in data["reply"]


@pytest.mark.asyncio
async def test_scenario_12_handle_ollama_unavailable():
    """Scenario 12: Handle Ollama being unavailable with graceful local fallback"""
    ollama = OllamaProvider()
    # Check fallback when model or service is offline
    fake_messages = [{"role": "user", "content": "Check CPU and RAM usage"}]
    # Run chat; should gracefully fall back to local engine without crashing
    res = await ollama.chat(fake_messages)
    assert "reply" in res
    assert res.get("tools_executed") is not None


@pytest.mark.asyncio
async def test_scenario_13_reject_unauthorized_destructive_actions():
    """Scenario 13: Reject unauthorized destructive actions & unapproved executables"""
    # 1. Block unapproved arbitrary executable
    bad_launch = launch_application("trojan_virus.exe", dry_run=True)
    assert bad_launch["success"] is False
    assert "not in the approved application registry" in bad_launch["error"]

    # 2. Block file write to C:\Windows
    safe, msg = is_path_safe(r"C:\Windows\System32\hacked.dll", for_writing=True)
    assert safe is False
    assert "protected Windows system directory" in msg


def test_scenario_14_confirm_no_false_success_messages():
    """Scenario 14: Confirm that false success messages cannot occur"""
    # Launching a non-approved or non-existent app must strictly report failure
    res = launch_application("non_existent_fake_tool.exe")
    assert res["success"] is False
    assert res["verification_status"] == "failed"
    assert "not in the approved application registry" in res["error"]
