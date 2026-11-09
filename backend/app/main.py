from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from .config import settings
from .routers import health, config_api, chat, tools_api, providers_api, tasks_api, approval_api

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="INAYA Multimodal Autonomous Personal AI Assistant",
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API routers
app.include_router(health.router)
app.include_router(config_api.router)
app.include_router(chat.router)
app.include_router(tools_api.router)
app.include_router(providers_api.router)
app.include_router(tasks_api.router)
app.include_router(approval_api.router)

# Mount frontend static distribution if built
dist_path = settings.FRONTEND_DIST
if dist_path.exists() and (dist_path / "index.html").exists():
    app.mount("/assets", StaticFiles(directory=dist_path / "assets"), name="assets")

    @app.get("/")
    async def serve_frontend_root():
        return FileResponse(dist_path / "index.html")

else:
    @app.get("/")
    async def fallback_root():
        return {
            "message": "INAYA AI Backend is online and operational.",
            "health_endpoint": "/api/health",
            "docs": "/docs",
        }
