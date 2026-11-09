from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Dict, Any
from ..tools.registry import TOOL_DEFINITIONS, execute_tool

router = APIRouter(prefix="/api/tools", tags=["Tools"])


class ToolRunRequest(BaseModel):
    name: str = Field(..., description="Tool name to execute")
    arguments: Dict[str, Any] = Field(default_factory=dict, description="Validated tool arguments")


@router.get("")
async def list_tools():
    """Returns the list of approved, validated tools with schemas."""
    return {"tools": TOOL_DEFINITIONS}


@router.post("/run")
async def run_tool(request: ToolRunRequest):
    """Executes an approved tool with argument validation."""
    result = execute_tool(request.name, request.arguments)
    if not result.get("success", False) and "error" in result:
        # We return the execution result with HTTP 200 or 400 depending on outcome
        return {"status": "error", "result": result}
    return {"status": "success", "result": result}
