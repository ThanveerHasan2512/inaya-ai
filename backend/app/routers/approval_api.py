from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List
from ..safety.policy import _PENDING_APPROVALS, approve_request, reject_request

router = APIRouter(prefix="/api/approvals", tags=["Safety Approvals"])


@router.get("", response_model=Dict[str, Any])
async def list_pending_approvals():
    """Lists all actions currently awaiting human confirmation."""
    pending = [r for r in _PENDING_APPROVALS.values() if r.get("status") == "pending"]
    return {
        "pending_count": len(pending),
        "approvals": pending,
    }


@router.post("/{request_id}/approve", response_model=Dict[str, Any])
async def handle_approve(request_id: str):
    """Approves a sensitive or destructive action."""
    res = approve_request(request_id)
    if not res:
        raise HTTPException(status_code=404, detail=f"Approval request '{request_id}' not found.")
    return {"status": "approved", "request": res}


@router.post("/{request_id}/reject", response_model=Dict[str, Any])
async def handle_reject(request_id: str):
    """Rejects a sensitive or destructive action."""
    res = reject_request(request_id)
    if not res:
        raise HTTPException(status_code=404, detail=f"Approval request '{request_id}' not found.")
    return {"status": "rejected", "request": res}
