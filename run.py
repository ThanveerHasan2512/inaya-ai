import sys
import uvicorn
from pathlib import Path

# Ensure backend directory is in python sys.path
BASE_DIR = Path(__file__).resolve().parent
backend_dir = BASE_DIR / "backend"
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

if __name__ == "__main__":
    from app.config import settings

    print(f"==================================================")
    print(f"  Starting {settings.PROJECT_NAME} v{settings.VERSION}")
    print(f"  Personalized for: {settings.USER_NAME}")
    print(f"  Active Provider : {settings.ACTIVE_PROVIDER}")
    print(f"  Web Interface   : http://{settings.HOST}:{settings.PORT}")
    print(f"  API Docs        : http://{settings.HOST}:{settings.PORT}/docs")
    print(f"==================================================")

    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        app_dir=str(backend_dir),
        reload=False,
    )
