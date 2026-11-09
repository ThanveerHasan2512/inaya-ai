
import json
import httpx
from typing import Dict, Any, List, Optional

from .base import BaseProvider
from ..intent import extract_intent
from ...config import settings
from ...tools.registry import TOOL_DEFINITIONS, execute_tool


MAX_TOOL_ROUNDS = 3


class OllamaProvider(BaseProvider):

    @property
    def name(self) -> str:
        return "ollama"

    async def is_available(self) -> Dict[str, Any]:
        """
        Check whether Ollama is reachable and the configured model
        is installed.
        """
        url = f"{settings.OLLAMA_BASE_URL.rstrip('/')}/api/tags"

        try:
            async with httpx.AsyncClient(timeout=3.0) as client:
                res = await client.get(url)

                if res.status_code == 200:
                    data = res.json()
                    models = [
                        m.get("name")
                        for m in data.get("models", [])
                    ]

                    model_found = any(
                        settings.OLLAMA_MODEL in m for m in models
                    )

                    return {
                        "available": True,
                        "status": "online",
                        "model": settings.OLLAMA_MODEL,
                        "installed_models": models,
                        "model_ready": model_found,
                        "message": (
                            f"Ollama is reachable. Model "
                            f"'{settings.OLLAMA_MODEL}' "
                            + (
                                "is available."
                                if model_found
                                else f"is not yet pulled. Run: "
                                     f"ollama pull {settings.OLLAMA_MODEL}"
                            )
                        ),
                    }

                return {
                    "available": False,
                    "status": "error",
                    "code": res.status_code,
                    "message": (
                        f"Ollama returned HTTP status {res.status_code}"
                    ),
                }

        except httpx.ConnectError:
            return {
                "available": False,
                "status": "offline",
                "message": (
                    f"Ollama server is not running at "
                    f"{settings.OLLAMA_BASE_URL}."
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
        messages: List[Dict[str, Any]],
        tools: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:

        check = await self.is_available()

        if not check.get("available") or not check.get("model_ready"):
            from .local_engine import LocalEngineProvider
            local_fallback = LocalEngineProvider()
            res = await local_fallback.chat(messages, tools)
            res["reply"] = f"[Local Assistant Engine: Ollama offline] {res['reply']}"
            return res

        url = f"{settings.OLLAMA_BASE_URL.rstrip('/')}/api/chat"

        system_prompt = """
You are INAYA, a personal AI assistant created by Thanveer Hasan.

Your identity:
- Your name is INAYA.
- Your creator is Thanveer Hasan.
- Never introduce yourself as Qwen or Alibaba Cloud.
- Be intelligent, helpful and professional.

Your responsibilities:
- Understand natural-language instructions.
- Help with programming, research and productivity.
- Use available tools when a user requests an action.
- Only use tools provided to you.
- Never invent tools or tool results.
- Never claim an action succeeded unless its result confirms success.
- Explain failures honestly.
- Ask for confirmation before consequential or destructive actions.

When a user asks you to open an approved application,
use the launch_application tool instead of explaining
how the user can open it manually.

Always identify yourself as INAYA when asked about your identity.
"""

        available_tools = (
            tools if tools is not None else TOOL_DEFINITIONS
        )

        # Convert INAYA tool definitions to Ollama's tool format.
        ollama_tools = [
            {
                "type": "function",
                "function": tool,
            }
            for tool in available_tools
        ]

        conversation_messages = [
            {"role": "system", "content": system_prompt},
            *messages,
        ]

        tools_executed = []

        try:
            async with httpx.AsyncClient(timeout=120.0) as client:

                # Allow up to three tool-execution rounds,
                # followed by one final AI response.
                for round_number in range(MAX_TOOL_ROUNDS + 1):

                    payload = {
                        "model": settings.OLLAMA_MODEL,
                        "messages": conversation_messages,
                        "stream": False,
                    }

                    if ollama_tools:
                        payload["tools"] = ollama_tools

                    res = await client.post(url, json=payload)

                    if res.status_code != 200:
                        return {
                            "reply": (
                                f"Ollama returned error: "
                                f"HTTP {res.status_code}"
                            ),
                            "provider": "ollama",
                            "tools_executed": tools_executed,
                            "error": res.text,
                        }

                    data = res.json()
                    assistant_message = data.get("message", {})
                    tool_calls = assistant_message.get(
                        "tool_calls", []
                    )

                    # No tool requested: check if user had a clear computer action intent that the model missed
                    if not tool_calls:
                        content_reply = assistant_message.get("content", "No response generated.")
                        last_user_msg = messages[-1].get("content", "") if messages else ""
                        analysis = extract_intent(last_user_msg)
                        tool_name = analysis.get("tool")
                        if tool_name and analysis.get("confidence", 0) >= 0.8:
                            try:
                                res = execute_tool(tool_name, analysis.get("arguments", {}))
                                tools_executed.append({
                                    "name": tool_name,
                                    "tool": tool_name,
                                    "arguments": analysis.get("arguments", {}),
                                    "args": analysis.get("arguments", {}),
                                    "result": res,
                                })
                                action_detail = res.get("details") or res.get("message") or f"Executed {tool_name}."
                                return {
                                    "reply": f"{action_detail}\n\n{content_reply}",
                                    "provider": "ollama",
                                    "tools_executed": tools_executed,
                                }
                            except Exception:
                                pass

                        return {
                            "reply": content_reply,
                            "provider": "ollama",
                            "tools_executed": tools_executed,
                        }

                    # Stop if the maximum number of rounds is reached.
                    if round_number == MAX_TOOL_ROUNDS:
                        return {
                            "reply": (
                                "I reached the tool execution limit. "
                                "Please check the actions already completed."
                            ),
                            "provider": "ollama",
                            "tools_executed": tools_executed,
                        }

                    # Preserve the assistant's tool-call message.
                    conversation_messages.append(assistant_message)

                    approved_names = {
                        tool["name"] for tool in TOOL_DEFINITIONS
                    }

                    # Execute each requested approved tool.
                    for tool_call in tool_calls:

                        function = tool_call.get("function", {})
                        tool_name = function.get("name", "")
                        arguments = function.get("arguments", {})

                        if isinstance(arguments, str):
                            try:
                                arguments = json.loads(arguments)
                            except json.JSONDecodeError:
                                arguments = None

                        if (
                            tool_name not in approved_names
                            or not isinstance(arguments, dict)
                        ):
                            result = {
                                "success": False,
                                "error": (
                                    "Unknown tool or invalid arguments."
                                ),
                            }
                        else:
                            try:
                                result = execute_tool(
                                    tool_name,
                                    arguments
                                )
                            except Exception as e:
                                result = {
                                    "success": False,
                                    "error": str(e),
                                }

                        tools_executed.append({
                            "name": tool_name,
                            "tool": tool_name,
                            "arguments": arguments,
                            "args": arguments,
                            "result": result,
                        })

                        # Send the actual execution result back to Ollama.
                        conversation_messages.append({
                            "role": "tool",
                            "tool_name": tool_name,
                            "content": json.dumps(
                                result,
                                ensure_ascii=False
                            ),
                        })

        except Exception as e:
            return {
                "reply": (
                    f"Failed communicating with Ollama: {str(e)}"
                ),
                "provider": "ollama",
                "tools_executed": tools_executed,
                "error": str(e),
            }

        return {
            "reply": "INAYA could not complete the requested operation.",
            "provider": "ollama",
            "tools_executed": tools_executed,
        }
