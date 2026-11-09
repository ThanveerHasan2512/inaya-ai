import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app

@pytest.mark.asyncio
async def test_server_endpoints():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Health
        res_health = await client.get("/api/health")
        assert res_health.status_code == 200
        assert res_health.json()["status"] == "ok"

        # 2. Config
        res_cfg = await client.get("/api/config")
        assert res_cfg.status_code == 200
        assert res_cfg.json()["project_name"] == "INAYA AI"

        # 3. Chat Greeting
        res_chat = await client.post("/api/chat", json={"message": "Hello INAYA"})
        assert res_chat.status_code == 200
        assert "INAYA" in res_chat.json()["reply"]

        # 4. Chat System Telemetry
        res_sys = await client.post("/api/chat", json={"message": "system status"})
        assert res_sys.status_code == 200
        assert "CPU Usage" in res_sys.json()["reply"]

        # 5. Frontend Root
        res_root = await client.get("/")
        assert res_root.status_code == 200
        assert "INAYA" in res_root.text

if __name__ == "__main__":
    import httpx
    try:
        c = httpx.Client(base_url="http://127.0.0.1:8000")
        print("Live Health:", c.get("/api/health").json())
        print("Live Root:", c.get("/").status_code)
    except Exception as e:
        print("Server not running on port 8000:", e)
