import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app

@pytest.mark.asyncio
async def test_notepad_tool():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.post("/api/chat", json={"message": "open notepad"})
        assert res.status_code == 200
        data = res.json()
        assert len(data["tools_executed"]) == 1
        assert data["tools_executed"][0]["tool"] == "launch_application"
        assert data["tools_executed"][0]["args"]["app_name"] == "notepad"
        assert "Notepad" in data["reply"]

if __name__ == "__main__":
    import httpx
    try:
        c = httpx.Client(base_url="http://127.0.0.1:8000")
        r = c.post("/api/chat", json={"message": "open notepad"})
        print("Live status:", r.status_code, r.json())
    except Exception as e:
        print("Live server offline:", e)
