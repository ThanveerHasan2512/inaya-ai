from fastapi import APIRouter
from pydantic import BaseModel, Field
from ..brain.providers.factory import list_providers_status, get_provider

router = APIRouter(prefix="/api/providers", tags=["Providers"])


class TestProviderRequest(BaseModel):
    provider: str = Field(..., description="Provider name to test (ollama, gemini, openai, local)")


@router.get("")
async def get_providers():
    """Lists current reachability and status for all configured providers."""
    return await list_providers_status()


@router.post("/test")
async def test_provider(request: TestProviderRequest):
    """Tests connection to a specific provider."""
    provider = get_provider(request.provider)
    status = await provider.is_available()
    return {
        "provider": provider.name,
        "result": status,
    }
