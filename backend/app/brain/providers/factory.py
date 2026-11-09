from typing import Dict, Any
from .base import BaseProvider
from .ollama import OllamaProvider
from .gemini import GeminiProvider
from .openai_provider import OpenAIProvider
from .local_engine import LocalEngineProvider
from ...config import settings

_PROVIDERS: Dict[str, BaseProvider] = {
    "local": LocalEngineProvider(),
    "ollama": OllamaProvider(),
    "gemini": GeminiProvider(),
    "openai": OpenAIProvider(),
}


def get_provider(name: str = None) -> BaseProvider:
    provider_name = (name or settings.ACTIVE_PROVIDER).lower()
    return _PROVIDERS.get(provider_name, _PROVIDERS["local"])


async def list_providers_status() -> Dict[str, Any]:
    statuses = {}
    for name, provider in _PROVIDERS.items():
        statuses[name] = await provider.is_available()
    return {
        "active_provider": settings.ACTIVE_PROVIDER,
        "providers": statuses,
    }
