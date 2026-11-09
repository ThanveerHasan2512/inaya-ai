# INAYA – Multimodal Autonomous Personal AI Assistant

> **Vision**: *Your Personal AI That Understands Anything You Want to Achieve and Gets It Done For You.*  
> **Personalized for**: **Thanveer**  
> **Mandatory Location**: `D:\INAYA`

---

## 🏛️ System Architecture

INAYA combines a responsive futuristic desktop HUD interface (React + Vite) with a high-performance Python FastAPI orchestration backend, verified Windows automation tool registry, and multi-provider AI adapters.

```
D:\INAYA\
├── backend\
│   └── app\
│       ├── brain\
│       │   └── providers\       # LocalEngine, Ollama, Gemini, OpenAI
│       ├── routers\             # health, chat, tools, providers, config
│       ├── tools\               # Verified Windows desktop automation registry
│       ├── config.py            # Environment configuration (Pydantic / dotenv)
│       └── main.py              # FastAPI server & static SPA mounting
├── INAYA-UI\                    # React 18 + Vite frontend
│   ├── src\                     # Holographic Core Orb, Audio Waveform, Chat, Telemetry
│   ├── dist\                    # Production build served by FastAPI at http://127.0.0.1:8000
│   └── package.json
├── venv\                        # Project-isolated Python virtual environment
├── tests\                       # Acceptance & unit tests (pytest)
├── run.py                       # Unified single-command launcher
├── .env                         # Local environment secrets (ignored by Git)
├── .env.example                 # Environment template
└── README.md                    # Project documentation
```

---

## ⚡ Quick Start (Windows PowerShell)

### 1. Prerequisites
- **Python**: 3.12+ (or 3.14) installed
- **Node.js**: v20+ / v24+ with npm installed
- **Workspace**: Everything is maintained locally inside `D:\INAYA`

### 2. Launch INAYA Server
Open Windows PowerShell and run:

```powershell
Set-Location 'D:\INAYA'
.\venv\Scripts\python.exe run.py
```

Open your browser to:
👉 **[http://127.0.0.1:8000](http://127.0.0.1:8000)** (or **http://localhost:8000**)

The FastAPI backend serves the React interface and the `/api` endpoints simultaneously.

---

## 🧪 Running Automated Tests

Run the test suite using pytest from the project virtual environment:

```powershell
Set-Location 'D:\INAYA'
.\venv\Scripts\python.exe -m pytest tests -v
```

All 9 acceptance tests verify:
- Health endpoint (`/api/health`) and real hardware telemetry (CPU, RAM, D: disk space, uptime)
- Security: ensuring zero secret API keys are leaked via `/api/config`
- Safe Windows tool registry execution (dry-runs for Notepad and Calculator)
- Blocking of arbitrary unapproved executables or scripts
- Local assistant chat and provider status reporting

---

## 🛡️ Windows Tool Registry & Security

To prevent arbitrary or dangerous execution from untrusted model outputs, INAYA uses a **strict allowlist registry**:
- **Approved Applications**:
  - `Notepad` (`notepad.exe`)
  - `Calculator` (`calc.exe`)
  - `File Explorer` (`explorer.exe`)
  - `Command Prompt` (`cmd.exe`)
- Arbitrary executable paths, command chaining, and untrusted scripts are blocked and rejected with an explicit error message.
- Tool arguments are strictly validated before execution.
- Safe dry-run mode is supported for non-destructive testing.

---

## 🤖 AI Provider Configuration

INAYA defaults to the **Local Assistant Engine** (offline, instant, deterministic Windows automation). You can configure additional providers in `D:\INAYA\.env`:

### 1. Local Assistant (Default)
- No internet or external service required.
- Handles application launching ("Open Notepad", "Open Calculator"), system telemetry ("System status"), time/date, and assistance.

### 2. Local Ollama (100% Private Offline LLM)
- Install Ollama for Windows from [ollama.com](https://ollama.com).
- Download a model: `ollama pull llama3`
- In `D:\INAYA\.env`:
  ```env
  ACTIVE_PROVIDER=ollama
  OLLAMA_BASE_URL=http://localhost:11434
  OLLAMA_MODEL=llama3
  ```

### 3. Google Gemini (Cloud)
- In `D:\INAYA\.env`:
  ```env
  ACTIVE_PROVIDER=gemini
  GEMINI_API_KEY=your_gemini_api_key_here
  GEMINI_MODEL=gemini-2.0-flash
  ```

### 4. OpenAI (Cloud)
- In `D:\INAYA\.env`:
  ```env
  ACTIVE_PROVIDER=openai
  OPENAI_API_KEY=your_openai_api_key_here
  OPENAI_MODEL=gpt-4o-mini
  ```
