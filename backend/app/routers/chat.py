
import datetime

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

from ..brain.providers.factory import get_provider
from ..tools.registry import TOOL_DEFINITIONS
from ..database.memory import get_conversation, save_message

router = APIRouter(prefix="/api", tags=["Chat"])


class ChatRequest(BaseModel):
    message: str = Field(
        ..., min_length=1, max_length=4000,
        description="User message text"
    )
    provider: Optional[str] = Field(
        None, description="Optional provider override"
    )
    session_id: str = Field(
        default="default",
        min_length=1,
        max_length=100,
        description="Conversation session identifier"
    )


class ChatResponse(BaseModel):
    reply: str
    provider: str
    tools_executed: List[Dict[str, Any]] = []
    timestamp: str


@router.post("/chat", response_model=ChatResponse)
async def handle_chat(request: ChatRequest):
    """
    Processes messages using MongoDB persistent conversation memory.
    """

    message_text = request.message.strip()

    if not message_text:
        raise HTTPException(
            status_code=400,
            detail="Message cannot be empty."
        )

    session_id = request.session_id
    provider = get_provider(request.provider)

    try:
        # Retrieve previous conversation from MongoDB.
        conversation = get_conversation(session_id)

        # Add the latest user message.
        conversation.append({
            "role": "user",
            "content": message_text
        })

        # Keep only the latest 20 messages.
        conversation = conversation[-20:]

        # Send conversation to the AI provider.
        result = await provider.chat(
            messages=conversation,
            tools=TOOL_DEFINITIONS
        )

        reply = result.get(
            "reply",
            "No response generated."
        )

        # Save user message and AI response permanently.
        save_message(session_id, "user", message_text)
        save_message(session_id, "assistant", reply)

        return ChatResponse(
            reply=reply,
            provider=result.get("provider", provider.name),
            tools_executed=result.get("tools_executed", []),
            timestamp=datetime.datetime.now().isoformat()
        )

    except Exception as error:
        return ChatResponse(
            reply=f"Error processing request: {str(error)}",
            provider=provider.name,
            tools_executed=[],
            timestamp=datetime.datetime.now().isoformat()
        )
