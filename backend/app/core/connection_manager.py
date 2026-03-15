"""WebSocket Connection Manager — manages dashboard and transcript connections."""

from __future__ import annotations

import json

from fastapi import WebSocket


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
