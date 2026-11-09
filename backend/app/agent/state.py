import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class TaskStatus(str, Enum):
    PENDING = "pending"
    PLANNING = "planning"
    RUNNING = "running"
    AWAITING_APPROVAL = "awaiting_approval"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PAUSED = "paused"


class SubTask(BaseModel):
    id: str = Field(default_factory=lambda: f"step-{uuid.uuid4().hex[:6]}")
    description: str
    tool: str
    args: Dict[str, Any] = Field(default_factory=dict)
    status: TaskStatus = TaskStatus.PENDING
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    requires_approval: bool = False
    verification_rule: Optional[str] = None  # e.g., "process_running", "telemetry_present", "file_exists"
    verified: bool = False
    observations: Dict[str, Any] = Field(default_factory=dict)
    started_at: Optional[str] = None
    completed_at: Optional[str] = None


class TaskPlan(BaseModel):
    task_id: str = Field(default_factory=lambda: f"task-{uuid.uuid4().hex[:8]}")
    objective: str
    session_id: str = "default"
    status: TaskStatus = TaskStatus.PENDING
    subtasks: List[SubTask] = Field(default_factory=list)
    current_step_index: int = 0
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    completed_at: Optional[str] = None
    error: Optional[str] = None
    final_report: Optional[str] = None

    def get_current_subtask(self) -> Optional[SubTask]:
        if 0 <= self.current_step_index < len(self.subtasks):
            return self.subtasks[self.current_step_index]
        return None

    def advance_step(self) -> Optional[SubTask]:
        self.current_step_index += 1
        self.updated_at = datetime.now(timezone.utc).isoformat()
        return self.get_current_subtask()

    def mark_subtask_running(self, step_id: str):
        for sub in self.subtasks:
            if sub.id == step_id:
                sub.status = TaskStatus.RUNNING
                sub.started_at = datetime.now(timezone.utc).isoformat()
                break
        self.status = TaskStatus.RUNNING
        self.updated_at = datetime.now(timezone.utc).isoformat()

    def mark_subtask_completed(self, step_id: str, result: Dict[str, Any], verified: bool = True):
        for sub in self.subtasks:
            if sub.id == step_id:
                sub.status = TaskStatus.COMPLETED
                sub.result = result
                sub.verified = verified
                sub.completed_at = datetime.now(timezone.utc).isoformat()
                break
        self.updated_at = datetime.now(timezone.utc).isoformat()

    def mark_subtask_failed(self, step_id: str, error: str):
        for sub in self.subtasks:
            if sub.id == step_id:
                sub.status = TaskStatus.FAILED
                sub.error = error
                sub.completed_at = datetime.now(timezone.utc).isoformat()
                break
        self.status = TaskStatus.FAILED
        self.error = f"Subtask '{step_id}' failed: {error}"
        self.completed_at = datetime.now(timezone.utc).isoformat()
        self.updated_at = datetime.now(timezone.utc).isoformat()

    def cancel(self, reason: str = "User cancelled task."):
        self.status = TaskStatus.CANCELLED
        self.error = reason
        self.completed_at = datetime.now(timezone.utc).isoformat()
        self.updated_at = datetime.now(timezone.utc).isoformat()
        for sub in self.subtasks:
            if sub.status in [TaskStatus.PENDING, TaskStatus.RUNNING, TaskStatus.AWAITING_APPROVAL]:
                sub.status = TaskStatus.CANCELLED
                sub.error = reason

    def mark_completed(self, report: str):
        self.status = TaskStatus.COMPLETED
        self.final_report = report
        self.completed_at = datetime.now(timezone.utc).isoformat()
        self.updated_at = datetime.now(timezone.utc).isoformat()
