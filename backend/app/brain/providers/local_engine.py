import datetime
from typing import Dict, Any, List, Optional
from .base import BaseProvider
from ..intent import extract_intent
from ...tools.registry import execute_tool
from ...tools.apps import APPROVED_APPLICATIONS
from ...config import settings


class LocalEngineProvider(BaseProvider):
    @property
    def name(self) -> str:
        return "local"

    async def is_available(self) -> Dict[str, Any]:
        return {
            "available": True,
            "status": "online",
            "model": "built-in-local-assistant",
            "message": "Local assistant engine is active and ready for Windows commands.",
        }

    async def chat(
        self,
        messages: List[Dict[str, str]],
        tools: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        if not messages:
            return {
                "reply": "Hello! How can I assist you?",
                "provider": "local",
                "tools_executed": [],
            }

        last_content = messages[-1].get("content", "").strip()
        analysis = extract_intent(last_content)
        intent = analysis.get("intent")
        tools_executed = []

        # 1. Launch Approved Application
        if intent == "LAUNCH_APP":
            app_name = analysis.get("arguments", {}).get("app_name")
            result = execute_tool("launch_application", {"app_name": app_name})
            tools_executed.append({
                "tool": "launch_application",
                "args": {"app_name": app_name},
                "result": result,
            })

            display_name = result.get("app_name", app_name.title())
            if result.get("success"):
                pid_info = f" (PID: {result['pid']})" if result.get("pid") else ""
                reply = f"I have launched {display_name} for you, {settings.USER_NAME}{pid_info}."
            else:
                reply = f"Could not launch {display_name}: {result.get('error')}"

            return {
                "reply": reply,
                "provider": "local",
                "tools_executed": tools_executed,
            }

        # 2. Launch Unapproved Application (Security Protection)
        if intent == "LAUNCH_UNAPPROVED_APP":
            app_name = analysis.get("arguments", {}).get("app_name", "unknown")
            approved_list = sorted(list({v["name"] for v in APPROVED_APPLICATIONS.values()}))
            reply = (
                f"For security, INAYA only launches verified applications from the approved registry. "
                f"'{app_name}' is not in the allowlist.\n\n"
                f"Approved applications available: {', '.join(approved_list)}."
            )
            return {
                "reply": reply,
                "provider": "local",
                "tools_executed": [],
            }

        # 3. System Telemetry / Vitals
        if intent == "SYSTEM_TELEMETRY":
            telemetry = execute_tool("get_system_telemetry", {})
            tools_executed.append({
                "tool": "get_system_telemetry",
                "args": {},
                "result": telemetry,
            })
            reply = (
                f"System Telemetry for your PC, {settings.USER_NAME}:\n"
                f"• CPU Usage: {telemetry.get('cpu_usage')}%\n"
                f"• RAM Usage: {telemetry.get('ram_usage')}%\n"
                f"• D: Drive Free Space: {telemetry.get('d_drive_free_gb')} GB / {telemetry.get('d_drive_total_gb')} GB\n"
                f"• System Uptime: {telemetry.get('uptime')}"
            )
            return {
                "reply": reply,
                "provider": "local",
                "tools_executed": tools_executed,
            }

        # 4. Time & Date
        if intent == "TIME_DATE":
            now = datetime.datetime.now()
            time_str = now.strftime("%I:%M %p")
            date_str = now.strftime("%A, %B %d, %Y")
            reply = f"The current time is {time_str} on {date_str}."
            return {
                "reply": reply,
                "provider": "local",
                "tools_executed": [],
            }

        # 5. Greetings
        if intent == "GREETING":
            reply = f"Hello {settings.USER_NAME}! I am INAYA, your personal AI desktop assistant. How can I assist you today?"
            return {
                "reply": reply,
                "provider": "local",
                "tools_executed": [],
            }

        # 6. Capabilities & Help
        if intent == "HELP":
            approved_list = sorted(list({v["name"] for v in APPROVED_APPLICATIONS.values()}))
            reply = (
                f"Here is what I can do for you right now, {settings.USER_NAME}:\n"
                f"• Windows Applications: 'Open Notepad', 'Launch Calculator', 'Open File Explorer', 'Start Chrome', 'Open Edge', 'Open VS Code', 'Command Prompt'\n"
                f"• System Diagnostics: 'System status', 'Check CPU and RAM', 'D: drive storage'\n"
                f"• Clock & Calendar: 'What time is it?', 'Current date'\n"
                f"• Controlled Execution: All commands are strictly validated against an approved allowlist.\n\n"
                f"Approved applications: {', '.join(approved_list)}."
            )
            return {
                "reply": reply,
                "provider": "local",
                "tools_executed": [],
            }

        # 7. Fallback for open-ended or unrecognized instructions
        reply = (
            f"I received: \"{last_content}\".\n"
            f"I am currently operating in the verified Local Assistant mode. "
            f"I can control approved Windows applications (Notepad, Calculator, File Explorer, Chrome, Edge, VS Code) "
            f"and report live system telemetry. You can ask me to open any of these or type 'Help' for guidance."
        )
        return {
            "reply": reply,
            "provider": "local",
            "tools_executed": [],
        }
