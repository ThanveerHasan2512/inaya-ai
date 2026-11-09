import re
from typing import List, Dict, Any, Optional
from .state import TaskPlan, SubTask, TaskStatus
from ..brain.intent import extract_intent
from ..tools.registry import TOOL_DEFINITIONS
from ..tools.apps import APPROVED_APPLICATIONS
from ..safety.policy import evaluate_action_safety


class TaskPlanner:
    """
    Decomposes natural language user goals into structured multi-step execution plans.
    """

    def __init__(self):
        self.available_tools = {t["name"]: t for t in TOOL_DEFINITIONS}

    def _split_compound_goal(self, goal: str) -> List[str]:
        """
        Splits multi-action compound sentences into atomic instruction segments.
        Handles: "then", "and then", "after that", "also", "and", semicolons, periods.
        """
        text = goal.strip()
        if not text:
            return []

        delimiters = [
            r"\s+and\s+then\s+",
            r"\s+then\s+",
            r"\s+after\s+that\s+",
            r";\s*",
            r"\n+",
        ]
        combined_pattern = "|".join(delimiters)
        raw_parts = re.split(combined_pattern, text, flags=re.IGNORECASE)

        action_verbs = [
            "open", "launch", "start", "run", "close", "exit", "quit",
            "check", "show", "get", "tell me", "display", "bring up",
            "create", "make", "read", "write", "search", "list", "copy", "move", "rename"
        ]
        segments = []

        for part in raw_parts:
            part = part.strip()
            if not part:
                continue

            and_split = re.split(r"\s+and\s+", part, flags=re.IGNORECASE)
            if len(and_split) > 1:
                current_clause = ""
                for clause in and_split:
                    clause_lower = clause.lower().strip()
                    has_action = any(clause_lower.startswith(v) or f" {v} " in f" {clause_lower} " for v in action_verbs)
                    if has_action and current_clause:
                        segments.append(current_clause.strip())
                        current_clause = clause
                    elif current_clause:
                        current_clause += f" and {clause}"
                    else:
                        current_clause = clause
                if current_clause:
                    segments.append(current_clause.strip())
            else:
                segments.append(part)

        return segments if segments else [text]

    def plan_subtask_from_text(self, step_text: str, step_index: int) -> Optional[SubTask]:
        """
        Maps an atomic natural language step to a concrete tool and argument schema.
        """
        analysis = extract_intent(step_text)
        tool_name = analysis.get("tool")
        arguments = analysis.get("arguments", {})

        if tool_name and tool_name in self.available_tools:
            requires_approval, severity, reason = evaluate_action_safety(tool_name, arguments)

            # Friendly step description
            if tool_name == "launch_application":
                desc = f"Launch application: {arguments.get('app_name', '').title()}"
                rule = "process_running"
            elif tool_name == "close_application":
                desc = f"Close application: {arguments.get('app_name', '').title()}"
                rule = "tool_success"
            elif tool_name == "get_system_telemetry":
                desc = "Retrieve system telemetry (CPU, RAM, Disk, Uptime, Battery)"
                rule = "telemetry_present"
            elif tool_name == "create_file":
                desc = f"Create file at '{arguments.get('path', '')}'"
                rule = "file_exists"
            elif tool_name == "read_file":
                desc = f"Read file at '{arguments.get('path', '')}'"
                rule = "tool_success"
            elif tool_name == "write_file":
                desc = f"Write text to '{arguments.get('path', '')}'"
                rule = "tool_success"
            elif tool_name == "create_folder":
                desc = f"Create directory at '{arguments.get('path', '')}'"
                rule = "tool_success"
            elif tool_name == "open_path":
                desc = f"Open Windows path: '{arguments.get('path', '')}'"
                rule = "tool_success"
            else:
                desc = f"Execute {tool_name} ({arguments})"
                rule = "tool_success"

            return SubTask(
                id=f"step-{step_index + 1}",
                description=desc,
                tool=tool_name,
                args=arguments,
                status=TaskStatus.PENDING,
                verification_rule=rule,
                requires_approval=requires_approval,
            )

        return None

    def create_plan(self, objective: str, session_id: str = "default") -> TaskPlan:
        """
        Decomposes an objective into a structured TaskPlan.
        """
        plan = TaskPlan(
            objective=objective,
            session_id=session_id,
            status=TaskStatus.PLANNING,
        )

        segments = self._split_compound_goal(objective)
        subtasks = []

        for idx, segment in enumerate(segments):
            sub = self.plan_subtask_from_text(segment, idx)
            if sub:
                subtasks.append(sub)

        if not subtasks:
            single_sub = self.plan_subtask_from_text(objective, 0)
            if single_sub:
                subtasks.append(single_sub)

        plan.subtasks = subtasks
        if subtasks:
            plan.status = TaskStatus.PENDING
        else:
            plan.status = TaskStatus.FAILED
            plan.error = f"Could not decompose goal into executable actions: '{objective}'"

        return plan
