import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app


@pytest.mark.asyncio
async def test_health_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "system" in data
        assert "cpu_usage" in data["system"]
        assert "ram_usage" in data["system"]
        assert "d_drive_free_gb" in data["system"]
        assert data["system"]["d_drive_free_gb"] > 0


@pytest.mark.asyncio
async def test_config_endpoint_no_secrets():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/config")
        assert response.status_code == 200
        data = response.json()
        assert data["project_name"] == "INAYA AI"
        assert "gemini" in data
        assert "openai" in data
        # Ensure no raw secret keys are exposed
        assert "GEMINI_API_KEY" not in data
        assert "OPENAI_API_KEY" not in data
