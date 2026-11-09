from fastapi import APIRouter
from ..config import settings

router = APIRouter(prefix="/api", tags=["Config"])


@router.get("/config")
async def get_config():
    """
    Returns public system settings safely without exposing secret keys.
    """
    return {
        "project_name": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "user_name": settings.USER_NAME,
        "active_provider": settings.ACTIVE_PROVIDER,
        "ollama": {
            "base_url": settings.OLLAMA_BASE_URL,
            "model": settings.OLLAMA_MODEL,
        },
        "gemini": {
            "configured": bool(settings.GEMINI_API_KEY.strip()),
            "model": settings.GEMINI_MODEL,
        },
        "openai": {
            "configured": bool(settings.OPENAI_API_KEY.strip()),
            "model": settings.OPENAI_MODEL,
            "base_url": settings.OPENAI_BASE_URL,
        },
    }
