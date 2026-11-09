import os
from pathlib import Path
from pydantic import BaseModel
from dotenv import load_dotenv

# Base directory for INAYA
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Load .env file from project root
dotenv_path = BASE_DIR / ".env"
load_dotenv(dotenv_path=dotenv_path, override=True)


class Settings(BaseModel):
    PROJECT_NAME: str = "INAYA AI"
    VERSION: str = "1.0.0"
    BASE_DIR: Path = BASE_DIR
    HOST: str = os.getenv("HOST", "127.0.0.1")
    PORT: int = int(os.getenv("PORT", "8000"))
    USER_NAME: str = os.getenv("USER_NAME", "Thanveer")

    # Provider settings
    ACTIVE_PROVIDER: str = os.getenv("ACTIVE_PROVIDER", "local")  # local | ollama | gemini | openai
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "llama3")

    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")

    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    OPENAI_BASE_URL: str = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")

    # Frontend dist directory
    FRONTEND_DIST: Path = BASE_DIR / "INAYA-UI" / "dist"

    # CORS origins
    ALLOWED_ORIGINS: list[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
    ]


settings = Settings()
