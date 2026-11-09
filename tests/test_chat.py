import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app


@pytest.mark.asyncio
async def test_chat_greeting():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post("/api/chat", json={"message": "Hello INAYA"})
        assert response.status_code == 200
        data = response.json()
        assert "INAYA" in data["reply"]
        assert data["provider"] == "local"


@pytest.mark.asyncio
async def test_chat_system_status():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post("/api/chat", json={"message": "system status"})
        assert response.status_code == 200
        data = response.json()
        assert "CPU Usage" in data["reply"]
        assert len(data["tools_executed"]) == 1
        assert data["tools_executed"][0]["tool"] == "get_system_telemetry"


@pytest.mark.asyncio
async def test_providers_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/providers")
        assert response.status_code == 200
        data = response.json()
        assert "providers" in data
        assert "ollama" in data["providers"]
        assert "local" in data["providers"]
        assert data["providers"]["local"]["available"] is True
