"""Chat endpoints — transcript ingestion, processing, and Q&A."""

from fastapi import APIRouter

from app.api.schemas import TranscriptInput, QueryInput

router = APIRouter()


def _get_deps():
    from app.main import pipeline, manager
    return pipeline, manager


@router.post("/api/transcript")
async def add_transcript(input: TranscriptInput):
    pipeline, manager = _get_deps()
    entry = pipeline.add_transcript(input.speaker, input.text, input.phase)
    await manager.broadcast_all("transcript", entry)
    return {"status": "ok", "entry": entry}


@router.post("/api/process")
async def trigger_process(phase: int | None = None):
    pipeline, _ = _get_deps()
    result = await pipeline.process(phase=phase)
    return result


@router.post("/api/query")
async def handle_query(input: QueryInput):
    """Interactive Q&A — runs a focused clinical query through the pipeline."""
    pipeline, _ = _get_deps()
    result = await pipeline.query(input.question, speaker=input.speaker)
    return result
