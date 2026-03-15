"""FastAPI application — Ambient Dx Intelligence backend entrypoint."""

from __future__ import annotations

import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import USE_CACHE, USE_IRIS
from app.core.pipeline import Pipeline
from app.core.connection_manager import ConnectionManager
from app.api import health, patient, chat, demo, websocket

# ─── Singleton instances ───

pipeline = Pipeline(use_cache=USE_CACHE, use_iris=USE_IRIS)
manager = ConnectionManager()


async def _pipeline_broadcast(event_type: str, data: dict):
    await manager.broadcast_all(event_type, data)


pipeline.set_broadcast_callback(_pipeline_broadcast)

# ─── FastAPI App ───

app = FastAPI(title="Ambient Dx Intelligence", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(patient.router)
app.include_router(chat.router)
app.include_router(demo.router)
app.include_router(websocket.router)


if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("PORT", 8000))
    print(f"\n[+] Ambient Dx Intelligence -- Backend starting on port {port}")
    if USE_CACHE:
        print("[*] Using pre-cached responses (--cached mode)")
    elif USE_IRIS:
        print("[*] Using IRIS retrieval backend (--iris mode)")
    else:
        print("[*] Using ChromaDB retrieval (default mode)")
    print(f"[>] API docs: http://localhost:{port}/docs\n")
    uvicorn.run("app.main:app", host="0.0.0.0", port=port)
