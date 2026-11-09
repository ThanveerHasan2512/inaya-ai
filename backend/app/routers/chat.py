import datetime
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from ..brain.providers.factory import get_provider
from ..tools.registry import TOOL_DEFINITIONS

router = APIRouter(prefix="/api", tags=["Chat"])


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=4000, description="User message text")
    provider: Optional[str] = Field(None, description="Optional override for active provider")


class ChatResponse(BaseModel):
    reply: str
    provider: str
    tools_executed: List[Dict[str, Any]] = []
    timestamp: str


@router.post("/chat", response_model=ChatResponse)
async def handle_chat(request: ChatRequest):
    """
    Receives user natural-language input, processes it through the active AI provider
    or deterministic local engine, and executes verified tools when needed.
    """
    message_text = request.message.strip()
    if not message_text:
        raise HTTPException(status_code=400, detail="Message cannot be empty.")

    provider = get_provider(request.provider)
    messages = [{"role": "user", "content": message_text}]

    try:
        result = await provider.chat(messages=messages, tools=TOOL_DEFINITIONS)
        return ChatResponse(
            reply=result.get("reply", "No response generated."),
            provider=result.get("provider", provider.name),
            tools_executed=result.get("tools_executed", []),
            timestamp=datetime.datetime.now().isoformat(),
        )
    except Exception as e:
        return ChatResponse(
            reply=f"Error executing request: {str(e)}",
            provider=provider.name,
            tools_executed=[],
            timestamp=datetime.datetime.now().isoformat(),
        )
