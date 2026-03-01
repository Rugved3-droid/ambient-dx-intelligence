# Ambient Dx Intelligence

**Real-time Ambient Clinical Diagnostic Intelligence System**
MIT Grand Hack 2026 — Virtual Diagnostic Interface Track

## What It Does

Listens to clinical conversations in real-time, understands what the medical team is discussing, retrieves relevant patient data from the EMR, and displays diagnostic reasoning on a clinical monitoring dashboard.

**Demo scenario:** Patient Robert Chen, 67M, POD#6 right TKA, develops acute hypotension. The system catches that he has a **documented history of Heparin-Induced Thrombocytopenia (HIT)** from 2023 and is currently on a heparin drip with platelets dropping >50% — a critical safety finding missed by the clinical team.

## Tech Stack

- **Backend:** Python FastAPI + WebSocket
- **Frontend:** React (Vite) + Tailwind CSS
- **Speech-to-text:** Deepgram API
- **Intent Recognition:** OpenAI GPT-4o-mini
- **Diagnostic Reasoning:** Anthropic Claude Sonnet
- **Vector DB:** ChromaDB (in-memory)

## Quick Start

### Prerequisites

- Python 3.11-3.13 (ChromaDB doesn't support 3.14)
- Node.js 18+
- API keys for Deepgram, OpenAI, and Anthropic

### Setup

1. **Clone and configure:**
   ```bash
   cd ambient-dx
   cp .env.example .env
   # Edit .env with your API keys
   ```

2. **Install backend dependencies:**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Install frontend dependencies:**
   ```bash
   cd frontend
   npm install
   ```

### Run

**Option A — Start script (recommended):**
```bash
# Linux/Mac
chmod +x start.sh
./start.sh

# Windows
start.bat
```

**Option B — Manual:**
```bash
# Terminal 1: Backend
cd backend
source venv/bin/activate
python main.py

# Terminal 2: Frontend
cd frontend
npm run dev
```

**Option C — Cached mode (no API calls, instant demo):**
```bash
./start.sh --cached
# or
cd backend && python main.py --cached
```

### Access

- **Dashboard:** http://localhost:3000
- **API Docs:** http://localhost:8000/docs

## Demo

1. Open http://localhost:3000
2. Click **"Start Demo"** in the bottom bar
3. Watch the 3-phase rapid response unfold:
   - **Phase 1:** Rapid response called — acute hypotension
   - **Phase 2:** Team discusses GI bleed
   - **Phase 3:** Team discusses PE → **System catches HIT** (the "holy shit" moment)

## Architecture

```
Audio/Transcript
      ↓
[GPT-4o-mini] Intent Recognition
      ↓
[ChromaDB] RAG Retrieval ← Patient EMR Data
      ↓
[Claude Sonnet] Diagnostic Reasoning  ←→  [Claude Sonnet] Safety Cross-Reference
      ↓
WebSocket → React Dashboard
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/health` | Health check |
| GET | `/api/patient` | Raw patient data |
| POST | `/api/transcript` | Add transcript segment |
| POST | `/api/process` | Trigger pipeline processing |
| GET | `/api/state` | Current pipeline state |
| GET | `/api/results` | Latest diagnostic results |
| POST | `/api/demo/start` | Start full 3-phase demo |
| POST | `/api/demo/phase/{n}` | Run single demo phase |
| POST | `/api/demo/reset` | Reset all state |
| WS | `/ws/dashboard` | Real-time dashboard updates |
| WS | `/ws/transcript` | Real-time transcript feed |
