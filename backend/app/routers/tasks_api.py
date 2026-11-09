from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
from ..agent.orchestrator import orchestrator
from ..agent.state import TaskPlan, TaskStatus

router = APIRouter(prefix="/api/tasks", tags=["Autonomous Tasks"])


class CreateTaskRequest(BaseModel):
    objective: str = Field(..., min_length=1, max_length=2000, description="Natural language user objective")
    session_id: str = Field(default="default", description="Session identifier")
    run_sync: bool = Field(default=True, description="Whether to execute synchronously before returning")


class CancelTaskRequest(BaseModel):
    reason: str = Field(default="User cancelled task", description="Cancellation reason")


@router.post("", response_model=Dict[str, Any])
async def create_and_run_task(request: CreateTaskRequest, background_tasks: BackgroundTasks):
    """
    Receives a natural language objective, plans execution steps,
    and runs the autonomous cycle:
    RECEIVE -> UNDERSTAND -> PLAN -> OBSERVE -> EXECUTE -> VERIFY -> REPORT
    """
    objective = request.objective.strip()
    if not objective:
        raise HTTPException(status_code=400, detail="Objective cannot be empty.")

    plan = await orchestrator.receive_and_plan(objective=objective, session_id=request.session_id)

    if plan.status == TaskStatus.FAILED:
        return {
            "status": "failed",
            "task": plan.model_dump(),
            "error": plan.error,
        }

    if request.run_sync:
        executed_plan = await orchestrator.run_plan(plan)
        return {
            "status": executed_plan.status.value,
            "task": executed_plan.model_dump(),
        }
    else:
        # Schedule in background
        background_tasks.add_task(orchestrator.run_plan, plan)
        return {
            "status": "started",
            "task": plan.model_dump(),
        }


@router.get("", response_model=Dict[str, Any])
async def list_tasks(limit: int = 20):
    """Lists recent tasks and execution states."""
    return {"tasks": orchestrator.list_tasks(limit=limit)}


@router.get("/{task_id}", response_model=Dict[str, Any])
async def get_task_status(task_id: str):
    """Retrieves live state and verification results for a task."""
    plan = orchestrator.get_task(task_id)
    if not plan:
        raise HTTPException(status_code=404, detail=f"Task '{task_id}' not found.")
    return {"task": plan.model_dump()}


@router.post("/{task_id}/cancel", response_model=Dict[str, Any])
async def cancel_task(task_id: str, request: Optional[CancelTaskRequest] = None):
    """Cancels a running task safely."""
    reason = request.reason if request else "User requested cancellation"
    success = await orchestrator.cancel_task(task_id, reason=reason)
    if not success:
        raise HTTPException(status_code=404, detail=f"Task '{task_id}' not found.")
    return {
        "status": "cancelled",
        "task_id": task_id,
        "message": f"Task '{task_id}' successfully cancelled.",
    }
