import datetime
from typing import Dict, Any, List, Optional
from .base import BaseProvider
from ..intent import extract_intent
from ...tools.registry import execute_tool
from ...tools.apps import APPROVED_APPLICATIONS
from ...agent.orchestrator import orchestrator
from ...agent.state import TaskStatus
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

        # Check for multi-step / compound instructions (e.g. "Open Notepad and check CPU")
        plan = await orchestrator.receive_and_plan(last_content)
        if plan.status != TaskStatus.FAILED and len(plan.subtasks) > 1:
            executed_plan = await orchestrator.run_plan(plan)
            tools_exec = []
            for sub in executed_plan.subtasks:
                tools_exec.append({
                    "tool": sub.tool,
                    "name": sub.tool,
                    "args": sub.args,
                    "arguments": sub.args,
                    "result": sub.result,
                })
            return {
                "reply": executed_plan.final_report or f"Completed {len(executed_plan.subtasks)} operations for you, {settings.USER_NAME}.",
                "provider": "local",
                "tools_executed": tools_exec,
            }

        analysis = extract_intent(last_content)
        intent = analysis.get("intent")
        tool_name = analysis.get("tool")
        arguments = analysis.get("arguments", {})
        tools_executed = []

        # 1. Launch Approved Application
        if intent == "LAUNCH_APP":
            app_name = arguments.get("app_name")
            result = execute_tool("launch_application", {"app_name": app_name})
            tools_executed.append({
                "tool": "launch_application",
                "name": "launch_application",
                "args": {"app_name": app_name},
                "arguments": {"app_name": app_name},
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
            app_name = arguments.get("app_name", "unknown")
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
                "name": "get_system_telemetry",
                "args": {},
                "arguments": {},
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
                f"• Windows Applications: 'Open Notepad', 'Launch Calculator', 'Open File Explorer', 'Start Chrome', 'Open Edge', 'Open VS Code', 'Close Notepad'\n"
                f"• Files & Folders: 'Create file test.txt with Hello', 'Read file notes.txt', 'Create folder my_project', 'List files in D:\\INAYA'\n"
                f"• System Diagnostics: 'System status', 'Check CPU and RAM', 'Running processes', 'System info'\n"
                f"• Web & Coding: 'Search the web for ...', 'Create Python project ...', 'Open website ...'\n\n"
                f"Approved applications: {', '.join(approved_list)}."
            )
            return {
                "reply": reply,
                "provider": "local",
                "tools_executed": [],
            }

        # 7. Generic Tool Execution (Files, Browser, Coding, System tools)
        if tool_name:
            result = execute_tool(tool_name, arguments)
            tools_executed.append({
                "tool": tool_name,
                "name": tool_name,
                "args": arguments,
                "arguments": arguments,
                "result": result,
            })
            details = result.get("details") or result.get("message") or f"Executed {tool_name} successfully."
            if not result.get("success", False):
                details = f"Action failed: {result.get('error', 'Unknown error')}"
            return {
                "reply": details,
                "provider": "local",
                "tools_executed": tools_executed,
            }

        # 8. Fallback for open-ended or unrecognized instructions
        reply = (
            f"I received: \"{last_content}\".\n"
            f"I am currently operating in the verified Local Assistant mode. "
            f"I can operate Windows applications (Notepad, VS Code, Calculator, File Explorer, Chrome, Edge), "
            f"manage files, and report system vitals. Type 'Help' to see available capabilities."
        )
        return {
            "reply": reply,
            "provider": "local",
            "tools_executed": [],
        }
