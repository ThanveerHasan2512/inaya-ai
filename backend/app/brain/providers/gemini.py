import httpx
from typing import Dict, Any, List, Optional
from .base import BaseProvider
from ...config import settings


class GeminiProvider(BaseProvider):
    @property
    def name(self) -> str:
        return "gemini"

    async def is_available(self) -> Dict[str, Any]:
        key = settings.GEMINI_API_KEY.strip()
        if not key:
            return {
                "available": False,
                "status": "not_configured",
                "message": "Gemini API key is not configured. Add GEMINI_API_KEY in .env.",
            }
        return {
            "available": True,
            "status": "configured",
            "model": settings.GEMINI_MODEL,
            "message": f"Gemini is configured with model {settings.GEMINI_MODEL}.",
        }

    async def chat(
        self,
        messages: List[Dict[str, str]],
        tools: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        check = await self.is_available()
        if not check.get("available"):
            return {
                "reply": "Google Gemini is not configured. Please set GEMINI_API_KEY in your .env file.",
                "provider": "gemini",
                "tools_executed": [],
                "error": check.get("message"),
            }

        # Convert simple chat format for Gemini REST API
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{settings.GEMINI_MODEL}:generateContent?key={settings.GEMINI_API_KEY}"
        contents = []
        for msg in messages:
            role = "user" if msg["role"] == "user" else "model"
            contents.append({"role": role, "parts": [{"text": msg["content"]}]})

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                res = await client.post(url, json={"contents": contents})
                if res.status_code == 200:
                    data = res.json()
                    candidates = data.get("candidates", [])
                    if candidates:
                        text = candidates[0].get("content", {}).get("parts", [{}])[0].get("text", "")
                        return {"reply": text, "provider": "gemini", "tools_executed": []}
                    return {"reply": "No response returned from Gemini.", "provider": "gemini", "tools_executed": []}
                return {
                    "reply": f"Gemini API returned error: {res.status_code}",
                    "provider": "gemini",
                    "tools_executed": [],
                    "error": res.text,
                }
        except Exception as e:
            return {
                "reply": f"Failed calling Gemini API: {str(e)}",
                "provider": "gemini",
                "tools_executed": [],
                "error": str(e),
            }
