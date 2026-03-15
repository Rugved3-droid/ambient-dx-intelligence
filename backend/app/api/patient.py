"""Patient data endpoints — state, results, transcript history, pre-arrival."""

from fastapi import APIRouter

router = APIRouter()


def _get_pipeline():
    from app.main import pipeline
    return pipeline


@router.get("/api/state")
async def get_state():
    return _get_pipeline().get_state()


@router.get("/api/patient")
async def get_patient():
    return _get_pipeline().pm.get_raw_patient_data()


@router.get("/api/pre-arrival")
async def get_pre_arrival():
    """Generate pre-arrival clinical intelligence from EMR data."""
    result = await _get_pipeline().generate_pre_arrival()
    return result


@router.get("/api/transcript/history")
async def get_transcript_history():
    return {"transcript": _get_pipeline().state.transcript_buffer}


@router.get("/api/results")
async def get_results():
    p = _get_pipeline()
    return {
        "intents": p.state.current_intents,
        "diagnostic": p.state.diagnostic_result,
        "safety": p.state.safety_result,
    }
