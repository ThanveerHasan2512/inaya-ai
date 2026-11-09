import os
import json
from pathlib import Path
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional

from .connection import database, client
from pymongo.errors import PyMongoError

MAX_HISTORY_MESSAGES = 20
LOCAL_STORE_PATH = Path(__file__).resolve().parent / "local_memory.json"

# In-memory fallback
_in_memory_sessions: Dict[str, List[Dict[str, Any]]] = {}
_in_memory_preferences: Dict[str, Any] = {}


def _load_local_store() -> Dict[str, Any]:
    if LOCAL_STORE_PATH.exists():
        try:
            with open(LOCAL_STORE_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"conversations": {}, "user_memories": {}}


def _save_local_store(data: Dict[str, Any]):
    try:
        with open(LOCAL_STORE_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception:
        pass


def _is_mongo_online() -> bool:
    try:
        client.admin.command("ping")
        return True
    except Exception:
        return False


def get_conversation(session_id: str) -> List[Dict[str, Any]]:
    """Retrieve conversation history from MongoDB, falling back to local file."""
    if _is_mongo_online():
        try:
            document = database["conversations"].find_one(
                {"session_id": session_id},
                {"_id": 0, "messages": 1}
            )
            if document:
                return document.get("messages", [])
        except PyMongoError:
            pass

    # Fallback to local store
    data = _load_local_store()
    return data.get("conversations", {}).get(session_id, [])


def save_message(session_id: str, role: str, content: str):
    """Save a message and limit stored history to MAX_HISTORY_MESSAGES."""
    message = {
        "role": role,
        "content": content,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    now = datetime.now(timezone.utc)

    # 1. Try MongoDB
    if _is_mongo_online():
        try:
            database["conversations"].update_one(
                {"session_id": session_id},
                {
                    "$push": {
                        "messages": {
                            "$each": [message],
                            "$slice": -MAX_HISTORY_MESSAGES
                        }
                    },
                    "$set": {"updated_at": now},
                    "$setOnInsert": {"created_at": now}
                },
                upsert=True
            )
            return
        except PyMongoError:
            pass

    # 2. Local store fallback
    data = _load_local_store()
    convs = data.setdefault("conversations", {})
    history = convs.setdefault(session_id, [])
    history.append(message)
    convs[session_id] = history[-MAX_HISTORY_MESSAGES:]
    _save_local_store(data)


def delete_conversation(session_id: str) -> bool:
    """Delete conversation history for a session."""
    deleted = False
    if _is_mongo_online():
        try:
            res = database["conversations"].delete_one({"session_id": session_id})
            deleted = res.deleted_count > 0
        except PyMongoError:
            pass

    data = _load_local_store()
    if session_id in data.get("conversations", {}):
        del data["conversations"][session_id]
        _save_local_store(data)
        deleted = True

    return deleted


def save_user_memory(key: str, value: Any):
    """Explicitly save a persistent user memory or preference."""
    data = _load_local_store()
    memories = data.setdefault("user_memories", {})
    memories[key] = {
        "value": value,
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }
    _save_local_store(data)


def get_user_memories() -> Dict[str, Any]:
    """Retrieve all saved user memories and preferences."""
    data = _load_local_store()
    return data.get("user_memories", {})


def delete_user_memory(key: str) -> bool:
    """Remove a specific user memory."""
    data = _load_local_store()
    if key in data.get("user_memories", {}):
        del data["user_memories"][key]
        _save_local_store(data)
        return True
    return False
