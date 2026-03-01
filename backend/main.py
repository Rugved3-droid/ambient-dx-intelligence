"""FastAPI application — REST + WebSocket endpoints for Ambient Dx Intelligence."""

from __future__ import annotations

import asyncio
import json
import os
import sys

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

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


if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("PORT", 8000))
    print(f"\n🏥 Ambient Dx Intelligence — Backend starting on port {port}")
    if USE_CACHE:
        print("📦 Using pre-cached responses (--cached mode)")
    print(f"🔗 API docs: http://localhost:{port}/docs\n")
    uvicorn.run(app, host="0.0.0.0", port=port)
