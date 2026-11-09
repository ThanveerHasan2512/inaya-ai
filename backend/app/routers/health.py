import datetime
from fastapi import APIRouter
from ..config import settings
from ..tools.system import get_system_telemetry

router = APIRouter(prefix="/api", tags=["Health"])


@router.get("/health")
async def health_check():
    telemetry = get_system_telemetry()
    return {
        "status": "ok",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "user_name": settings.USER_NAME,
        "active_provider": settings.ACTIVE_PROVIDER,
        "system": telemetry,
        "timestamp": datetime.datetime.now().isoformat(),
    }
