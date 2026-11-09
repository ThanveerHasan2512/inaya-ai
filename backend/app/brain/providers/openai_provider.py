import httpx
from typing import Dict, Any, List, Optional
from .base import BaseProvider
from ...config import settings


class OpenAIProvider(BaseProvider):
    @property
    def name(self) -> str:
        return "openai"

    async def is_available(self) -> Dict[str, Any]:
        key = settings.OPENAI_API_KEY.strip()
        if not key:
            return {
                "available": False,
                "status": "not_configured",
                "message": "OpenAI API key is not configured. Add OPENAI_API_KEY in .env.",
            }
        return {
            "available": True,
            "status": "configured",
            "model": settings.OPENAI_MODEL,
            "message": f"OpenAI is configured with model {settings.OPENAI_MODEL}.",
        }

    async def chat(
        self,
        messages: List[Dict[str, str]],
        tools: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        check = await self.is_available()
        if not check.get("available"):
            return {
                "reply": "OpenAI provider is not configured. Please set OPENAI_API_KEY in your .env file.",
                "provider": "openai",
                "tools_executed": [],
                "error": check.get("message"),
            }

        url = f"{settings.OPENAI_BASE_URL.rstrip('/')}/chat/completions"
        headers = {
            "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": settings.OPENAI_MODEL,
            "messages": messages,
        }

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                res = await client.post(url, headers=headers, json=payload)
                if res.status_code == 200:
                    data = res.json()
                    choice = data["choices"][0]["message"]
                    return {
                        "reply": choice.get("content", ""),
                        "provider": "openai",
                        "tools_executed": [],
                    }
                return {
                    "reply": f"OpenAI returned HTTP {res.status_code}",
                    "provider": "openai",
                    "tools_executed": [],
                    "error": res.text,
                }
        except Exception as e:
            return {
                "reply": f"Failed communicating with OpenAI: {str(e)}",
                "provider": "openai",
                "tools_executed": [],
                "error": str(e),
            }
