import httpx
import time

def test_live_chat_commands():
    client = httpx.Client(base_url="http://127.0.0.1:8000", timeout=10.0)

    # 1. Health check
    res_health = client.get("/api/health")
    assert res_health.status_code == 200
    print("[1] Health OK:", res_health.json()["status"], "CPU:", res_health.json()["system"]["cpu_usage"])

    # 2. Notepad command
    res_notepad = client.post("/api/chat", json={"message": "Can you please open Notepad?"})
    assert res_notepad.status_code == 200
    data_notepad = res_notepad.json()
    print("[2] Notepad:", data_notepad["reply"])
    assert len(data_notepad["tools_executed"]) == 1
    assert data_notepad["tools_executed"][0]["result"]["success"] is True

    # 3. Calculator command
    res_calc = client.post("/api/chat", json={"message": "I want to use calculator"})
    assert res_calc.status_code == 200
    data_calc = res_calc.json()
    print("[3] Calculator:", data_calc["reply"])
    assert len(data_calc["tools_executed"]) == 1
    assert data_calc["tools_executed"][0]["result"]["success"] is True

    # 4. File Explorer command
    res_explorer = client.post("/api/chat", json={"message": "Open File Explorer"})
    assert res_explorer.status_code == 200
    data_explorer = res_explorer.json()
    print("[4] Explorer:", data_explorer["reply"])
    assert len(data_explorer["tools_executed"]) == 1
    assert data_explorer["tools_executed"][0]["result"]["success"] is True

    # 5. System Status command
    res_sys = client.post("/api/chat", json={"message": "Show system status"})
    assert res_sys.status_code == 200
    data_sys = res_sys.json()
    print("[5] System Status:\n", data_sys["reply"])
    assert len(data_sys["tools_executed"]) == 1

    # 6. Unapproved application security block
    res_blocked = client.post("/api/chat", json={"message": "Launch unauthorized_game.exe"})
    assert res_blocked.status_code == 200
    data_blocked = res_blocked.json()
    print("[6] Security Block:\n", data_blocked["reply"])
    assert len(data_blocked["tools_executed"]) == 0
    assert "not in the allowlist" in data_blocked["reply"]

    # 7. Frontend assets delivered
    res_root = client.get("/")
    assert res_root.status_code == 200
    assert "INAYA" in res_root.text
    print("[7] Frontend UI successfully served at http://127.0.0.1:8000")

    print("\n>>> ALL PHASE 1 LIVE CHECKS PASSED SUCCESSFULLY! <<<")

if __name__ == "__main__":
    test_live_chat_commands()
