import httpx
from typing import Dict, Any, List, Optional
from .base import BaseProvider
from ...config import settings


class OllamaProvider(BaseProvider):
    @property
    def name(self) -> str:
        return "ollama"

    async def is_available(self) -> Dict[str, Any]:
        """
        Pings the Ollama instance at OLLAMA_BASE_URL to verify reachability
        and checks if the configured model is installed.
        """
        url = f"{settings.OLLAMA_BASE_URL.rstrip('/')}/api/tags"
        try:
            async with httpx.AsyncClient(timeout=3.0) as client:
                res = await client.get(url)
                if res.status_code == 200:
                    data = res.json()
                    models = [m.get("name") for m in data.get("models", [])]
                    model_found = any(settings.OLLAMA_MODEL in m for m in models)
                    return {
                        "available": True,
                        "status": "online",
                        "model": settings.OLLAMA_MODEL,
                        "installed_models": models,
                        "model_ready": model_found,
                        "message": (
                            f"Ollama is reachable. Model '{settings.OLLAMA_MODEL}' "
                            + ("is available." if model_found else f"is not yet pulled. Run: ollama pull {settings.OLLAMA_MODEL}")
                        ),
                    }
                return {
                    "available": False,
                    "status": "error",
                    "code": res.status_code,
                    "message": f"Ollama returned HTTP status {res.status_code}",
                }
        except httpx.ConnectError:
            return {
                "available": False,
                "status": "offline",
                "message": (
                    f"Ollama server is not running at {settings.OLLAMA_BASE_URL}. "
                    "To use local Ollama, start the Ollama application or service."
                ),
            }
        except Exception as e:
            return {
                "available": False,
                "status": "error",
                "message": f"Could not reach Ollama: {str(e)}",
            }

    async def chat(
        self,
        messages: List[Dict[str, str]],
        tools: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        check = await self.is_available()
        if not check.get("available") or not check.get("model_ready"):
            return {
                "reply": (
                    f"Local Ollama is currently unavailable: {check.get('message')}. "
                    "You can run commands locally using the built-in Windows assistant, or start Ollama."
                ),
                "provider": "ollama",
                "tools_executed": [],
                "error": check.get("message"),
            }

        url = f"{settings.OLLAMA_BASE_URL.rstrip('/')}/api/chat"
        payload = {
            "model": settings.OLLAMA_MODEL,
            "messages": messages,
            "stream": False,
        }

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                res = await client.post(url, json=payload)
                if res.status_code == 200:
                    data = res.json()
                    content = data.get("message", {}).get("content", "")
                    return {
                        "reply": content,
                        "provider": "ollama",
                        "tools_executed": [],
                    }
                else:
                    return {
                        "reply": f"Ollama returned error: HTTP {res.status_code}",
                        "provider": "ollama",
                        "tools_executed": [],
                        "error": res.text,
                    }
        except Exception as e:
            return {
                "reply": f"Failed communicating with Ollama: {str(e)}",
                "provider": "ollama",
                "tools_executed": [],
                "error": str(e),
            }
