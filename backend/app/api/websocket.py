"""WebSocket endpoints — dashboard, transcript, and Deepgram audio proxy."""

from __future__ import annotations

import asyncio
import json

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.config import DEEPGRAM_API_KEY
from app.demo.runner import run_demo, run_demo_phase

router = APIRouter()


def _get_deps():
    from app.main import pipeline, manager
    return pipeline, manager


@router.websocket("/ws/dashboard")
async def websocket_dashboard(ws: WebSocket):
    pipeline, manager = _get_deps()
    await manager.connect_dashboard(ws)
    try:
        while True:
            data = await ws.receive_text()
            msg = json.loads(data)
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
            elif msg.get("command") == "pre_arrival":
                asyncio.create_task(pipeline.generate_pre_arrival())
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


@router.websocket("/ws/transcript")
async def websocket_transcript(ws: WebSocket):
    pipeline, manager = _get_deps()
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


@router.websocket("/ws/audio")
async def websocket_audio(ws: WebSocket):
    """Proxy audio from browser to Deepgram for real-time transcription."""
    pipeline, manager = _get_deps()
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
