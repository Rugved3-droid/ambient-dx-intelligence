"""FastAPI application — REST + WebSocket endpoints for Ambient Dx Intelligence."""

from __future__ import annotations

import asyncio
import json
import os
import sys

from dotenv import load_dotenv
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

from pipeline import Pipeline
from demo import run_demo, run_demo_phase

# Check for --demo and --cached flags
USE_CACHE = "--cached" in sys.argv or "--cache" in sys.argv
pipeline = Pipeline(use_cache=USE_CACHE)

app = FastAPI(title="Ambient Dx Intelligence", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY", "")

# ─── Auto-Processing Debounce ───
# After live speech, wait for a pause then auto-trigger processing
auto_process_task: asyncio.Task | None = None


async def schedule_auto_process(delay: float = 5.0):
    """Debounced auto-processing — waits for silence then triggers pipeline."""
    global auto_process_task
    await asyncio.sleep(delay)
    if not pipeline.state.processing and len(pipeline.state.transcript_buffer) > 0:
        print("[*] Auto-processing transcript...")
        await pipeline.process()


def trigger_auto_process():
    """Cancel previous timer and start a new one."""
    global auto_process_task
    if auto_process_task and not auto_process_task.done():
        auto_process_task.cancel()
    auto_process_task = asyncio.create_task(schedule_auto_process())


# ─── WebSocket Connection Manager ───


class ConnectionManager:
    def __init__(self):
        self.dashboard_connections: list[WebSocket] = []
        self.transcript_connections: list[WebSocket] = []

    async def connect_dashboard(self, ws: WebSocket):
        await ws.accept()
        self.dashboard_connections.append(ws)

    async def connect_transcript(self, ws: WebSocket):
        await ws.accept()
        self.transcript_connections.append(ws)

    def disconnect_dashboard(self, ws: WebSocket):
        if ws in self.dashboard_connections:
            self.dashboard_connections.remove(ws)

    def disconnect_transcript(self, ws: WebSocket):
        if ws in self.transcript_connections:
            self.transcript_connections.remove(ws)

    async def broadcast_dashboard(self, event_type: str, data: dict):
        message = json.dumps({"type": event_type, "data": data})
        dead = []
        for ws in self.dashboard_connections:
            try:
                await ws.send_text(message)
            except Exception:
                dead.append(ws)
        for ws in dead:
            self.disconnect_dashboard(ws)

    async def broadcast_transcript(self, data: dict):
        message = json.dumps({"type": "transcript", "data": data})
        dead = []
        for ws in self.transcript_connections:
            try:
                await ws.send_text(message)
            except Exception:
                dead.append(ws)
        for ws in dead:
            self.disconnect_transcript(ws)

    async def broadcast_all(self, event_type: str, data: dict):
        await self.broadcast_dashboard(event_type, data)
        if event_type == "transcript":
            await self.broadcast_transcript(data)


manager = ConnectionManager()


# Set the broadcast callback on the pipeline
async def pipeline_broadcast(event_type: str, data: dict):
    await manager.broadcast_all(event_type, data)


pipeline.set_broadcast_callback(pipeline_broadcast)


# ─── REST Endpoints ───


class TranscriptInput(BaseModel):
    speaker: str
    text: str
    phase: int = 0


class QueryInput(BaseModel):
    question: str
    speaker: str = "Judge"


@app.get("/api/health")
async def health():
    return {"status": "ok", "service": "ambient-dx-intelligence"}


@app.post("/api/transcript")
async def add_transcript(input: TranscriptInput):
    entry = pipeline.add_transcript(input.speaker, input.text, input.phase)
    await manager.broadcast_all("transcript", entry)
    return {"status": "ok", "entry": entry}


@app.post("/api/process")
async def trigger_process(phase: int | None = None):
    result = await pipeline.process(phase=phase)
    return result


@app.post("/api/query")
async def handle_query(input: QueryInput):
    """Interactive Q&A — runs a focused clinical query through the pipeline."""
    result = await pipeline.query(input.question, speaker=input.speaker)
    return result


@app.get("/api/state")
async def get_state():
    return pipeline.get_state()


@app.get("/api/patient")
async def get_patient():
    return pipeline.pm.get_raw_patient_data()


@app.get("/api/transcript/history")
async def get_transcript_history():
    return {"transcript": pipeline.state.transcript_buffer}


@app.get("/api/results")
async def get_results():
    return {
        "intents": pipeline.state.current_intents,
        "diagnostic": pipeline.state.diagnostic_result,
        "safety": pipeline.state.safety_result,
    }


# ─── Demo Endpoints ───


@app.post("/api/demo/start")
async def start_demo(phase_delay: float = 8.0):
    """Start the full 3-phase demo."""
    asyncio.create_task(run_demo(pipeline, phase_delay=phase_delay))
    return {"status": "demo_started"}


@app.post("/api/demo/phase/{phase_num}")
async def run_single_phase(phase_num: int):
    """Run a single demo phase."""
    result = await run_demo_phase(pipeline, phase_num)
    return result


@app.post("/api/demo/reset")
async def reset_demo():
    """Reset all pipeline state."""
    pipeline.state.transcript_buffer = []
    pipeline.state.current_intents = {}
    pipeline.state.diagnostic_result = {}
    pipeline.state.safety_result = {}
    pipeline.state.phase = 0
    pipeline.state.processing = False
    pipeline.state.last_processed = 0
    await manager.broadcast_all("reset", {})
    return {"status": "reset"}


@app.post("/api/demo/toggle-cache")
async def toggle_cache():
    pipeline.state.use_cache = not pipeline.state.use_cache
    return {"use_cache": pipeline.state.use_cache}


# ─── WebSocket Endpoints ───


@app.websocket("/ws/dashboard")
async def websocket_dashboard(ws: WebSocket):
    await manager.connect_dashboard(ws)
    try:
        while True:
            data = await ws.receive_text()
            msg = json.loads(data)
            # Handle commands from frontend
            if msg.get("command") == "process":
                asyncio.create_task(pipeline.process(phase=msg.get("phase")))
            elif msg.get("command") == "query":
                asyncio.create_task(
                    pipeline.query(msg.get("question", ""), speaker=msg.get("speaker", "Judge"))
                )
            elif msg.get("command") == "demo_start":
                asyncio.create_task(
                    run_demo(pipeline, phase_delay=msg.get("phase_delay", 8.0))
                )
            elif msg.get("command") == "demo_phase":
                asyncio.create_task(
                    run_demo_phase(pipeline, msg.get("phase", 1))
                )
            elif msg.get("command") == "reset":
                pipeline.state.transcript_buffer = []
                pipeline.state.current_intents = {}
                pipeline.state.diagnostic_result = {}
                pipeline.state.safety_result = {}
                pipeline.state.phase = 0
                pipeline.state.processing = False
                await manager.broadcast_all("reset", {})
    except WebSocketDisconnect:
        manager.disconnect_dashboard(ws)


@app.websocket("/ws/transcript")
async def websocket_transcript(ws: WebSocket):
    await manager.connect_transcript(ws)
    try:
        while True:
            data = await ws.receive_text()
            msg = json.loads(data)
            if msg.get("type") == "transcript":
                entry = pipeline.add_transcript(
                    speaker=msg.get("speaker", "Unknown"),
                    text=msg.get("text", ""),
                    phase=msg.get("phase", 0),
                )
                await manager.broadcast_all("transcript", entry)
    except WebSocketDisconnect:
        manager.disconnect_transcript(ws)


# ─── Deepgram Audio Proxy WebSocket ───


@app.websocket("/ws/audio")
async def websocket_audio(ws: WebSocket):
    """Proxy audio from browser to Deepgram for real-time transcription."""
    await ws.accept()
    print("[Mic] Browser connected to /ws/audio")

    if not DEEPGRAM_API_KEY:
        print("[Mic] ERROR: No Deepgram API key!")
        await ws.send_json({"type": "error", "message": "Deepgram API key not configured"})
        await ws.close()
        return

    import websockets

    dg_url = (
        "wss://api.deepgram.com/v1/listen"
        "?model=nova-2"
        "&punctuate=true"
        "&smart_format=true"
        "&interim_results=true"
        "&utterance_end_ms=1500"
        "&vad_events=true"
        "&encoding=opus"
        "&sample_rate=48000"
    )

    dg_ws = None
    stop_event = asyncio.Event()

    try:
        print("[Mic] Connecting to Deepgram...")
        dg_ws = await websockets.connect(
            dg_url,
            additional_headers={"Authorization": f"Token {DEEPGRAM_API_KEY}"},
        )
        print("[Mic] Deepgram connected!")
        await ws.send_json({"type": "connected", "message": "Deepgram connected"})

        async def browser_to_deepgram():
            try:
                while not stop_event.is_set():
                    msg = await ws.receive()
                    if msg.get("type") == "websocket.receive":
                        if "bytes" in msg and msg["bytes"]:
                            await dg_ws.send(msg["bytes"])
                        elif "text" in msg and msg["text"]:
                            text_msg = json.loads(msg["text"])
                            if text_msg.get("type") == "close":
                                stop_event.set()
                                break
                    elif msg.get("type") == "websocket.disconnect":
                        stop_event.set()
                        break
            except (WebSocketDisconnect, Exception) as e:
                print(f"[Mic] browser_to_deepgram ended: {e}")
                stop_event.set()

        async def deepgram_to_browser():
            try:
                async for raw_msg in dg_ws:
                    if stop_event.is_set():
                        break
                    result = json.loads(raw_msg)
                    msg_type = result.get("type", "")

                    if msg_type == "Results":
                        channel = result.get("channel", {})
                        alternatives = channel.get("alternatives", [])
                        if alternatives:
                            transcript_text = alternatives[0].get("transcript", "")
                            confidence = alternatives[0].get("confidence", 0)
                            is_final = result.get("is_final", False)
                            speech_final = result.get("speech_final", False)

                            if transcript_text:
                                await ws.send_json({
                                    "type": "partial" if not speech_final else "final",
                                    "text": transcript_text,
                                    "is_final": is_final,
                                    "speech_final": speech_final,
                                    "confidence": confidence,
                                })

                                if speech_final and transcript_text.strip():
                                    print(f"[Mic] Final: {transcript_text.strip()}")
                                    entry = pipeline.add_transcript(
                                        "Live Speaker", transcript_text.strip(), phase=0
                                    )
                                    await manager.broadcast_all("transcript", entry)

                    elif msg_type == "UtteranceEnd":
                        await ws.send_json({"type": "utterance_end"})

            except Exception as e:
                print(f"[Mic] deepgram_to_browser ended: {e}")
                stop_event.set()

        await asyncio.gather(
            browser_to_deepgram(),
            deepgram_to_browser(),
            return_exceptions=True,
        )

    except Exception as e:
        print(f"[Mic] ERROR: {e}")
        try:
            await ws.send_json({"type": "error", "message": str(e)})
        except Exception:
            pass
    finally:
        print("[Mic] Cleaning up")
        if dg_ws:
            try:
                await dg_ws.close()
            except Exception:
                pass
        try:
            await ws.close()
        except Exception:
            pass


if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("PORT", 8000))
    print(f"\n[+] Ambient Dx Intelligence -- Backend starting on port {port}")
    if USE_CACHE:
        print("[*] Using pre-cached responses (--cached mode)")
    else:
        print("[*] Using LIVE API calls (real-time mode)")
    print(f"[>] API docs: http://localhost:{port}/docs\n")
    uvicorn.run(app, host="0.0.0.0", port=port)
