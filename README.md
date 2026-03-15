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
- **Data Platform:** InterSystems IRIS (structured SQL + vector search)
- **Data Standard:** FHIR R4 (ingestion via Bundle parser)
- **Fallback Vector DB:** ChromaDB (in-memory)

---

## Prerequisites — Install These First

You need four things installed on your computer before starting. If you already have any of these, skip that step.

### 1. Python (3.11 or newer)

Check if you have it:
```bash
python3 --version
```

If not installed, download from **https://www.python.org/downloads/** and run the installer. On Mac you can also use Homebrew:
```bash
brew install python@3.13
```

### 2. Node.js (18 or newer)

Check if you have it:
```bash
node --version
```

If not installed, download from **https://nodejs.org/** (pick the LTS version) and run the installer. On Mac you can also use Homebrew:
```bash
brew install node
```

### 3. Docker Desktop

Check if you have it:
```bash
docker --version
```

If not installed:
- **Mac:** Download from **https://www.docker.com/products/docker-desktop/** and drag the app to Applications. Open Docker Desktop and wait until the whale icon in the menu bar is steady (not animating).
- **Windows:** Download from the same link. You may need to enable WSL 2 — the installer will guide you.
- **Linux:** Follow https://docs.docker.com/engine/install/ for your distro.

> Docker is required for IRIS mode (the full InterSystems integration). If you just want to run the cached demo, you can skip Docker.

### 4. API Keys (for live AI mode)

You need keys from three services. If you only want to run the **cached demo** (pre-computed responses, no live AI), you can skip this step entirely.

| Service | Sign up | What it does |
|---------|---------|-------------|
| Deepgram | https://console.deepgram.com/signup | Speech-to-text |
| OpenAI | https://platform.openai.com/signup | Intent recognition (GPT-4o-mini) |
| Anthropic | https://console.anthropic.com/ | Diagnostic reasoning (Claude Sonnet) |

After signing up, create an API key on each platform's dashboard.

---

## Setup (One-Time)

### Step 1 — Clone and configure

```bash
git clone <your-repo-url>
cd ambient-dx-intelligence
```

Copy the example environment file:
```bash
cp .env.example .env
```

Open `.env` in any text editor and paste your API keys (skip this if using cached mode):
```
DEEPGRAM_API_KEY=your_actual_key_here
ANTHROPIC_API_KEY=your_actual_key_here
OPENAI_API_KEY=your_actual_key_here
```

Leave the IRIS settings at their defaults — they work out of the box with Docker.

### Step 2 — Install backend dependencies

```bash
pip install -r backend/requirements.txt
```

> **Tip:** If you prefer an isolated environment, create a virtual environment first:
> ```bash
> python3 -m venv venv
> source venv/bin/activate    # Mac/Linux
> # venv\Scripts\activate     # Windows
> pip install -r backend/requirements.txt
> ```
> If you use conda instead:
> ```bash
> conda create -n ambient_dx python=3.13 -y
> conda activate ambient_dx
> pip install -r backend/requirements.txt
> ```

### Step 3 — Install frontend dependencies

```bash
cd frontend
npm install
cd ..
```

### Step 4 — Set up IRIS (for IRIS mode only)

If you want the full InterSystems IRIS integration (recommended for the hackathon demo), make sure Docker Desktop is running, then:

```bash
# Start the IRIS container (runs in the background)
docker compose up -d

# Wait ~15 seconds for IRIS to initialize, then seed patient data
pip install -r backend/requirements.txt   # if not already done
python scripts/setup_iris.py              # loads from custom JSON
python scripts/setup_iris.py --fhir       # loads from FHIR R4 Bundle (same data, standards-compliant format)
```

You should see output ending with `IRIS setup complete!`. This only needs to be done once — the data persists until you remove the container.

---

## Running the Demo

### Option A — Cached Mode (easiest, no API keys needed)

Uses pre-computed AI responses. Instant, reliable, free. Best for testing the UI or if you don't have API keys.

**Using the start script:**
```bash
chmod +x start.sh     # first time only
./start.sh --cached
```

**Or manually (two terminals):**
```bash
# Terminal 1 — Backend
cd backend
python -m app.main --cached

# Terminal 2 — Frontend
cd frontend
npm run dev
```

### Option B — Default Mode (live AI, no Docker needed)

Uses ChromaDB in-memory for retrieval + live API calls to Deepgram, OpenAI, and Anthropic. Requires valid API keys in `.env`.

```bash
./start.sh
```

### Option C — IRIS Mode (full InterSystems integration)

Uses InterSystems IRIS for both structured SQL queries and vector search. This is the mode to show judges. Requires Docker + API keys.

```bash
# Make sure Docker Desktop is running and IRIS is seeded (see Step 4 above)
./start.sh --iris
```

**Windows users:** Use `start.bat` instead of `./start.sh`, or run the backend and frontend manually in two terminals.

---

## Using the Demo

### Open the app

Go to **http://localhost:3000** in your browser.

### The EMR view

You start on the **EHR Hyperspace** interface — this looks like a real hospital chart system. Browse around:
- **Storyboard** — patient summary with vitals, labs, problems
- **Flowsheets** — vital sign history
- **Results** — lab values across all timepoints
- **MAR** — medication list
- **Notes** — clinical notes (the 2023 HIT discharge summary is buried under Previous Encounters, 3 clicks deep — this is intentional)
- **Allergies** — notice that heparin allergy is **missing** (the system error the AI will catch)

### Launch the AI dashboard

Click the **"Launch Ambient Dx"** button (pulsing purple, bottom right corner). After the transition animation, you'll be on the AI diagnostic dashboard.

### Run the scripted demo

In the bottom control bar, click **"Analyze Now"** to start the 3-phase demo:

| Phase | What happens | What the AI shows |
|-------|-------------|-------------------|
| **Phase 1** | Rapid response called — acute hypotension, tachycardia | Retrieves vitals, labs, medications. Shows critical hemoglobin and platelet drops. |
| **Phase 2** | Clinical team discusses GI bleed as likely cause | AI adds GI bleed to differentials but also flags the platelet trend as suspicious. |
| **Phase 3** | Team considers PE → **AI catches HIT** | Safety alert fires: patient has documented HIT history from 2023, is actively on heparin, and platelets have dropped 63%. Recommends immediate heparin discontinuation. |

### Interactive mode

You can also:
- Click **"Live Mic"** to speak clinical questions in real time (requires Deepgram key)
- Type questions in the text input at the bottom of the Clinical Q&A panel (e.g., "What are the patient's platelets doing?")
- Click **"View EMR"** in the top bar to go back to the chart

### Reset

Click **"Clear"** in the bottom bar to reset all state and start over.

---

## Access Points

| URL | What | When |
|-----|------|------|
| http://localhost:3000 | Main dashboard | Always |
| http://localhost:8000/docs | Backend API docs (Swagger) | Always |
| http://localhost:52773/csp/sys/UtilHome.csp | IRIS Management Portal (login: demo / demo) | IRIS mode only |

---

## Architecture

```
Audio/Transcript
      ↓
[GPT-4o-mini] Intent Recognition
      ↓
[IRIS Hybrid RAG] ← Structured SQL (meds, labs, allergies, vitals)
      |             ← Vector Search (clinical notes, 384-dim embeddings)
      ↓
[Claude Sonnet] Diagnostic Reasoning  ←→  [Claude Sonnet] Safety Cross-Reference
      ↓
WebSocket → React Dashboard
```

### Backend Structure

```
backend/
  app/
    main.py               # FastAPI entrypoint — creates app, registers routers
    config.py              # Environment variables and CLI flags
    api/                   # HTTP + WebSocket route handlers
      health.py, patient.py, chat.py, demo.py, websocket.py, schemas.py
    core/                  # Orchestration
      pipeline.py          # Transcript → intent → RAG → reasoning pipeline
      connection_manager.py
    llm/                   # LLM wrappers (one file per task)
      intent.py, diagnostic.py, safety.py, answerer.py, pre_arrival.py
      clients.py, prompts.py, parser.py
    retrieval/             # RAG engine + concept-to-category mapping
      engine.py, categories.py
    data/                  # Patient data loading + cached demo responses
      patient_manager.py, fhir_parser.py, cached_responses.py
    storage/               # InterSystems IRIS database layer
      iris_db.py, iris_vector_store.py
    demo/                  # Scripted demo scenario
      script.py, runner.py
  eval/                    # Ragas RAG evaluation harness
    dataset.py             # 15-question golden test dataset
    run_ragas.py           # Evaluation runner (ChromaDB vs IRIS)
  data/                    # Patient EMR JSON + FHIR R4 Bundle
  scripts/                 # IRIS setup, FHIR generation, smoke tests
  requirements.txt
```

```
patient_robert_chen.json          patient_robert_chen_fhir.json
  (custom format)                      (FHIR R4 Bundle)
         │                                     │
         │   ┌─────────────────────────────────┘
         │   │  app/data/fhir_parser.py (--fhir flag)
         │   │      parses FHIR resources → same internal dict
         │   │
         ▼   ▼
app/data/patient_manager.py
         │
         ├──► app/storage/iris_db.py (5 structured tables)
         │        └──► SQL queries at runtime (exact facts)
         │
         └──► chunk_patient_data() (38 chunks)
                  └──► app/storage/iris_vector_store.py (embed + HNSW index)
                           └──► VECTOR_DOT_PRODUCT at runtime (semantic search)
                                    │
                                    ▼
                           app/retrieval/engine.py merges both → Claude
```

### IRIS Hybrid Retrieval

In `--iris` mode, the RAG engine uses two retrieval strategies from a single InterSystems IRIS instance:

- **Structured SQL** — exact clinical facts (medications, allergies, lab values, vitals, problem list) from 5 normalized IRIS tables
- **Vector search** — semantic similarity over 38 clinical note chunk embeddings (384-dim, sentence-transformers all-MiniLM-L6-v2) with HNSW index and `VECTOR_DOT_PRODUCT`

Both results are merged and deduplicated before being passed to the LLM for diagnostic reasoning.

---

## RAG Evaluation (Ragas)

We use [Ragas](https://docs.ragas.io/) to objectively measure retrieval and generation quality. A golden test dataset of 15 clinician-verified questions (with ground-truth answers derived from the patient chart and cached diagnostic outputs) is evaluated against four metrics using GPT-4o-mini as the LLM judge.

### Metrics

| Metric | What it measures |
|--------|-----------------|
| **Faithfulness** | Does the generated answer only use facts from the retrieved context? (higher = less hallucination) |
| **Context Recall** | Did retrieval find all the information needed to answer correctly? |
| **Context Precision** | Are the top-ranked retrieved chunks actually relevant? |
| **Factual Correctness** | Does the answer match the clinician-verified ground truth? |

### Results (ChromaDB backend)

| Metric | Score |
|--------|-------|
| Faithfulness | **0.84** |
| Context Precision | **0.70** |
| Context Recall | **0.64** |
| Factual Correctness | **0.55** |

**Per-question highlights:**

| Question | Faithfulness | Ctx Recall | Ctx Precision | Factual |
|----------|:-----------:|:----------:|:-------------:|:-------:|
| Show me the platelet trend | 1.00 | 1.00 | 0.96 | 0.62 |
| Does the patient have any allergies? | 1.00 | 1.00 | 0.81 | 0.88 |
| Is heparin safe for this patient? | 1.00 | 1.00 | 0.77 | 0.70 |
| What medications is the patient currently on? | 1.00 | 1.00 | 0.72 | 0.70 |
| Calculate the 4Ts score for HIT | 0.41 | 0.67 | 1.00 | 0.68 |
| What imaging has been done on this patient? | 1.00 | 0.00 | 0.00 | 0.36 |

Safety-critical queries (allergies, medications, HIT history, heparin safety) consistently achieve perfect context recall, meaning the RAG pipeline reliably surfaces the data needed for patient safety decisions. Clinical score calculations (Wells, 4Ts) show lower faithfulness because the LLM reasons beyond the retrieved chunks to compute scores — expected behavior for multi-step clinical reasoning.

### Running the evaluation

```bash
cd backend

# Full evaluation (retrieval + generation, ~3 min, ~$0.25):
TOKENIZERS_PARALLELISM=false python -m eval.run_ragas

# Retrieval-only (faster, cheaper — no GPT-4o generation):
TOKENIZERS_PARALLELISM=false python -m eval.run_ragas --retrieval-only

# Side-by-side ChromaDB vs IRIS (requires IRIS Docker container):
TOKENIZERS_PARALLELISM=false python -m eval.run_ragas --iris
```

Results are saved to `backend/eval/results.json` with per-question breakdowns.

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `python3: command not found` | Install Python from https://www.python.org/downloads/ |
| `node: command not found` | Install Node.js from https://nodejs.org/ |
| `docker: command not found` | Install Docker Desktop from https://www.docker.com/products/docker-desktop/ |
| `docker compose up` hangs or fails | Make sure Docker Desktop is open and the engine is running (whale icon steady in menu bar) |
| IRIS portal won't load at `localhost:52773` | Use the full URL: http://localhost:52773/csp/sys/UtilHome.csp |
| `pip install` fails on `intersystems-irispython` | This package is only needed for `--iris` mode. Use `--cached` mode if you can't install it. |
| `ModuleNotFoundError: No module named 'iris'` | You're running in `--iris` mode but `intersystems-irispython` isn't installed. Either install it or use `--cached`. |
| Backend won't start — missing API keys | Use `--cached` mode, which doesn't need any API keys. |
| Frontend shows "DISCONNECTED" | Make sure the backend is running first (`python -m app.main` in the backend folder). |
| `npm install` fails | Make sure Node.js 18+ is installed. Delete `frontend/node_modules` and `frontend/package-lock.json`, then run `npm install` again. |

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/health` | Health check |
| GET | `/api/patient` | Raw patient data |
| POST | `/api/transcript` | Add transcript segment |
| POST | `/api/process` | Trigger pipeline processing |
| POST | `/api/query` | Interactive clinical Q&A |
| GET | `/api/state` | Current pipeline state |
| GET | `/api/results` | Latest diagnostic results |
| GET | `/api/transcript/history` | Transcript history |
| POST | `/api/demo/start` | Start full 3-phase demo |
| POST | `/api/demo/phase/{n}` | Run single demo phase |
| POST | `/api/demo/reset` | Reset all state |
| POST | `/api/demo/toggle-cache` | Toggle cached responses |
| WS | `/ws/dashboard` | Real-time dashboard updates |
| WS | `/ws/transcript` | Real-time transcript feed |
| WS | `/ws/audio` | Deepgram audio proxy |
