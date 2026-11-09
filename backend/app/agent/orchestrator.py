import asyncio
from typing import Dict, Any, Optional, List
from .state import TaskPlan, SubTask, TaskStatus
from .planner import TaskPlanner
from ..tools.registry import execute_tool
from ..tools.apps import verify_process_running, APPROVED_APPLICATIONS
from ..config import settings


class AgentOrchestrator:
    """
    INAYA Autonomous Agent Engine.
    Executes the continuous cycle:
    RECEIVE -> UNDERSTAND -> PLAN -> OBSERVE -> EXECUTE -> VERIFY -> REPORT
    """

    def __init__(self):
        self.planner = TaskPlanner()
        self.active_tasks: Dict[str, TaskPlan] = {}

    def get_task(self, task_id: str) -> Optional[TaskPlan]:
        return self.active_tasks.get(task_id)

    def list_tasks(self, limit: int = 20) -> List[Dict[str, Any]]:
        return [t.model_dump() for t in list(self.active_tasks.values())[-limit:]]

    async def receive_and_plan(self, objective: str, session_id: str = "default") -> TaskPlan:
        """
        [RECEIVE -> UNDERSTAND -> PLAN]
        Parses user intent and builds an actionable multi-step plan.
        """
        plan = self.planner.create_plan(objective=objective, session_id=session_id)
        self.active_tasks[plan.task_id] = plan
        return plan

    async def observe_pre(self, subtask: SubTask) -> Dict[str, Any]:
        """
        [OBSERVE - Pre-execution]
        Inspects environmental state before executing a step to avoid repeating completed work.
        """
        obs = {}
        if subtask.tool == "launch_application":
            app_key = subtask.args.get("app_name", "").lower()
            app_info = APPROVED_APPLICATIONS.get(app_key)
            if app_info:
                existing_pid = verify_process_running(app_info.get("process_names", []))
                obs["process_already_running"] = existing_pid is not None
                obs["existing_pid"] = existing_pid

        subtask.observations["pre"] = obs
        return obs

    async def verify_execution(self, subtask: SubTask, result: Dict[str, Any]) -> bool:
        """
        [VERIFY - Post-execution verification]
        Confirms that the operation produced the intended real-world effect.
        """
        is_success = result.get("success", "error" not in result)
        if not is_success:
            return False

        rule = subtask.verification_rule
        if rule == "process_running":
            app_key = subtask.args.get("app_name", "").lower()
            app_info = APPROVED_APPLICATIONS.get(app_key)
            if app_info:
                # Allow a short grace period for Windows process creation if needed
                for _ in range(3):
                    pid = verify_process_running(app_info.get("process_names", []))
                    if pid:
                        subtask.observations["verified_pid"] = pid
                        return True
                    await asyncio.sleep(0.3)
                return False
            return True

        elif rule == "telemetry_present":
            required = ["cpu_usage", "ram_usage", "d_drive_free_gb"]
            return all(k in result for k in required)

        elif rule == "file_exists":
            filepath = subtask.args.get("path")
            return bool(filepath and os.path.exists(filepath))

        # Default verification: tool succeeded
        return result.get("success", True)

    def generate_report(self, plan: TaskPlan) -> str:
        """
        [REPORT]
        Synthesizes an executive natural language report of all executed actions.
        """
        completed = [s for s in plan.subtasks if s.status == TaskStatus.COMPLETED]
        failed = [s for s in plan.subtasks if s.status == TaskStatus.FAILED]

        lines = [f"INAYA Task Execution Report for {settings.USER_NAME}:"]
        lines.append(f"• Objective: \"{plan.objective}\"")
        lines.append(f"• Status: {plan.status.value.upper()}")
        lines.append(f"• Completed Operations: {len(completed)} / {len(plan.subtasks)}")

        for s in plan.subtasks:
            icon = "✓" if s.status == TaskStatus.COMPLETED else "✗"
            ver_text = " [Verified]" if s.verified else ""
            lines.append(f"  {icon} {s.description}{ver_text}")
            if s.result and s.result.get("message"):
                lines.append(f"     Details: {s.result['message']}")
            elif s.error:
                lines.append(f"     Error: {s.error}")

        return "\n".join(lines)

    async def execute_subtask(self, plan: TaskPlan, subtask: SubTask) -> bool:
        """
        [EXECUTE -> VERIFY] single subtask.
        """
        # Check if already completed
        if subtask.status == TaskStatus.COMPLETED and subtask.verified:
            return True

        # Check for task-level cancellation
        if plan.status == TaskStatus.CANCELLED:
            subtask.status = TaskStatus.CANCELLED
            return False

        plan.mark_subtask_running(subtask.id)

        # 1. Observe Pre
        pre_obs = await self.observe_pre(subtask)

        # 2. Execute tool
        try:
            result = execute_tool(subtask.tool, subtask.args)
        except Exception as exc:
            plan.mark_subtask_failed(subtask.id, str(exc))
            return False

        is_success = result.get("success", "error" not in result)
        if not is_success:
            err_msg = result.get("error", "Execution failed")
            plan.mark_subtask_failed(subtask.id, err_msg)
            return False

        # 3. Verify
        verified = await self.verify_execution(subtask, result)
        if not verified:
            err_msg = f"Post-action verification failed for tool '{subtask.tool}'."
            plan.mark_subtask_failed(subtask.id, err_msg)
            return False

        # Mark step complete
        plan.mark_subtask_completed(subtask.id, result=result, verified=True)
        return True

    async def run_plan(self, plan: TaskPlan) -> TaskPlan:
        """
        Executes the entire plan sequentially.
        """
        if plan.status == TaskStatus.FAILED:
            return plan

        plan.status = TaskStatus.RUNNING

        for subtask in plan.subtasks:
            if plan.status == TaskStatus.CANCELLED:
                break

            success = await self.execute_subtask(plan, subtask)
            if not success:
                # Stop further execution on failure
                break

            plan.advance_step()

        # Update final plan status and report
        if plan.status != TaskStatus.CANCELLED and plan.status != TaskStatus.FAILED:
            all_done = all(s.status == TaskStatus.COMPLETED for s in plan.subtasks)
            if all_done:
                report = self.generate_report(plan)
                plan.mark_completed(report)
            else:
                plan.status = TaskStatus.FAILED
                plan.error = "One or more subtasks did not complete."

        return plan

    async def cancel_task(self, task_id: str, reason: str = "User requested cancellation.") -> bool:
        plan = self.get_task(task_id)
        if not plan:
            return False
        plan.cancel(reason)
        return True


# Global orchestrator singleton instance
orchestrator = AgentOrchestrator()
