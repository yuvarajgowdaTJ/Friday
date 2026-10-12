# JARVIS V4 — Autonomous Desktop AI Assistant

![JARVIS V4 Banner](https://img.shields.io/badge/JARVIS-v4.0-00f3ff?style=for-the-badge) ![Python](https://img.shields.io/badge/Python-3.11%2B-blue?style=for-the-badge) ![React](https://img.shields.io/badge/React-18-purple?style=for-the-badge) ![FastAPI](https://img.shields.io/badge/FastAPI-0.110-emerald?style=for-the-badge)

**JARVIS V4** is a personal Windows desktop AI assistant inspired by JARVIS. Built with a Python FastAPI backend and a futuristic React + TypeScript HUD frontend, it features voice interaction, wake-word activation, safe computer control, long-term memory, screen vision understanding, live hardware monitoring, and multi-step autonomous task planning.

---

## 🌟 Key Features

1. **AI Brain Core**: Powered by OpenAI SDK (`gpt-4o`) with automatic offline mock fallback so all functionality works even without API keys.
2. **Voice Pipeline**: Real-time Speech-to-Text (STT) and Text-to-Speech (TTS) synthesis with "Hey Jarvis" wake-word detection.
3. **Computer Control & File System**: Safe app launching (Chrome, VS Code, Notepad, Calc, Explorer), process management, file search, and directory operations.
4. **Persistent Long-Term Memory**: SQLite database storing memories, user preferences, facts, and conversation history.
5. **Web Intelligence**: Real-time DuckDuckGo web search with citation parsing and information summarization.
6. **Multimodal Screen Vision**: High-resolution desktop screenshot capture analyzed via GPT-4 Vision for error diagnostics and screen explanation.
7. **Autonomous Multi-Step Agent**: Autonomous planner decomposing complex tasks into discrete action steps with execution bounds (max 10 steps) and audit logging.
8. **Security & Permission Engine**: Three-tiered security model (`SAFE`, `CONFIRMATION_REQUIRED`, `BLOCKED`) protecting system operations with interactive UI confirmation dialogs.
9. **Futuristic Command Center HUD**: Dark neon glassmorphism UI with interactive **AI Arc Reactor** core, audio visualizer waveform, live CPU/RAM/Disk hardware gauges, and memory manager.

---

## 📁 Architecture & Project Structure

```text
JARVIS-V4/
├── backend/
│   ├── main.py              # FastAPI server entry point & WebSocket manager
│   ├── config.py            # Environment settings and paths
│   ├── requirements.txt     # Python backend dependencies
│   ├── core/
│   │   ├── brain.py         # AI provider & offline brain engine
│   │   ├── agent.py         # Autonomous multi-step agent loop
│   │   ├── planner.py       # Task planner & step generator
│   │   ├── memory.py        # SQLite persistent memory manager
│   │   └── security.py      # Security policy engine
│   ├── voice/               # Voice synthesis (TTS), STT, and wake-word
│   ├── vision/              # Multimodal screen analyzer
│   ├── tools/               # Tool registry (Browser, Computer, Files, Screenshot, System)
│   ├── database/            # SQLAlchemy database setup and models
│   └── api/                 # REST API endpoints (/api/chat, /api/voice, /api/tools, etc.)
├── frontend/
│   ├── src/
│   │   ├── components/      # AIReactor, Waveform, SystemStats, ChatPanel, ToolActivity, etc.
│   │   ├── App.tsx          # Main HUD layout assembly
│   │   └── index.css        # Futuristic styling tokens & glowing animations
│   ├── package.json
│   └── vite.config.ts
├── tests/                   # Automated pytest unit & integration test suite
├── .env.example
├── README.md
└── start_jarvis.bat         # Single-click Windows startup script
```

---

## 🚀 Quick Start Guide

### Prerequisites
- **Python 3.11+** installed and added to system PATH.
- **Node.js v18+** installed.

### Installation

1. **Clone or Navigate to Project**:
   ```bash
   cd "C:\Users\Yuvaraj Gowda T J\.gemini\antigravity\scratch\JARVIS-V4"
   ```

2. **Backend Setup**:
   ```bash
   python -m pip install -r backend/requirements.txt
   ```

3. **Frontend Setup**:
   ```bash
   cd frontend
   npm install
   cd ..
   ```

4. **Environment Configuration**:
   Copy `.env.example` to `.env`:
   ```bash
   copy .env.example .env
   ```
   *Optional*: Add your `OPENAI_API_KEY=sk-...` inside `.env` or set it directly in the UI Settings modal.

---

## 💻 Launching JARVIS

To start both the Python backend and React HUD automatically:

```bash
start_jarvis.bat
```

Or run services manually in two separate terminal windows:

- **Backend**:
  ```bash
  python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
  ```
- **Frontend**:
  ```bash
  cd frontend
  npm run dev
  ```

Open your browser to: **`http://localhost:5173`**

---

## 🧪 Running Automated Tests

To execute the unit and integration test suite:

```bash
python -m pytest tests/
```

Test coverage includes:
- AI Brain response logic (`test_brain.py`)
- Memory CRUD & SQLite persistence (`test_memory.py`)
- Central Tool Registry & hardware diagnostics (`test_tools.py`)
- Security Engine policy evaluation (`test_security.py`)
- Autonomous Agent Task Planner (`test_planner.py`)
- FastAPI endpoints integration (`test_api.py`)

---

## 🛡️ Security & Permission Model

- **SAFE**: Read-only queries, web searches, hardware stats, screenshots, launching standard apps (executed automatically).
- **CONFIRMATION_REQUIRED**: File deletion, overwriting, file moves, terminating processes, custom terminal commands (requires user approval modal in HUD).
- **BLOCKED**: Dangerous system formatting, malware keywords, unauthorized secret theft (automatically denied).

---

## 💬 Example Voice & Chat Commands

- `"Hey Jarvis, what's my CPU usage?"`
- `"Open Chrome"`
- `"Open Notepad"`
- `"Remember that my main project is JARVIS"`
- `"What is my main project?"`
- `"Take a screenshot"`
- `"Look at my screen"` *(Triggers Vision Screen Analysis)*
- `"Find five AI internships and compare them"` *(Triggers Multi-step Agent Mode)*
