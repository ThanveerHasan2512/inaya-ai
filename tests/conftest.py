import os
import sys
from pathlib import Path

# Ensure unit tests default to deterministic local provider unless explicitly overridden
os.environ.setdefault("ACTIVE_PROVIDER", "local")

backend_dir = Path(__file__).resolve().parent.parent / "backend"
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))
