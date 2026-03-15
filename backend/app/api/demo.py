"""Demo control endpoints — start, phase, reset, toggle cache."""

import asyncio

from fastapi import APIRouter

from app.demo.runner import run_demo, run_demo_phase

router = APIRouter()


def _get_deps():
    from app.main import pipeline, manager
    return pipeline, manager


@router.post("/api/demo/start")
async def start_demo(phase_delay: float = 8.0):
    """Start the full 4-phase demo."""
    pipeline, _ = _get_deps()
    asyncio.create_task(run_demo(pipeline, phase_delay=phase_delay))
    return {"status": "demo_started"}


@router.post("/api/demo/phase/{phase_num}")
async def run_single_phase(phase_num: int):
    """Run a single demo phase."""
    pipeline, _ = _get_deps()
    result = await run_demo_phase(pipeline, phase_num)
    return result


@router.post("/api/demo/reset")
async def reset_demo():
    """Reset all pipeline state."""
    pipeline, manager = _get_deps()
    pipeline.state.transcript_buffer = []
    pipeline.state.current_intents = {}
    pipeline.state.diagnostic_result = {}
    pipeline.state.safety_result = {}
    pipeline.state.phase = 0
    pipeline.state.processing = False
    pipeline.state.last_processed = 0
    await manager.broadcast_all("reset", {})
    return {"status": "reset"}


@router.post("/api/demo/toggle-cache")
async def toggle_cache():
    pipeline, _ = _get_deps()
    pipeline.state.use_cache = not pipeline.state.use_cache
    return {"use_cache": pipeline.state.use_cache}
