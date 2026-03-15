"""Demo runner — executes the 4-phase scripted rapid response scenario."""

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING

from app.demo.script import DEMO_SCRIPT

if TYPE_CHECKING:
    from app.core.pipeline import Pipeline


async def run_demo(pipeline: Pipeline, phase_delay: float = 8.0):
    """Run the full 4-phase demo scenario.

    Phase 0: Pre-arrival intelligence (auto-generated before conversation)
    Phase 1-4: Scripted conversation with processing
    """
    await pipeline.broadcast("phase", {
        "phase": 0,
        "title": "Pre-Arrival Intelligence",
        "status": "started",
    })

    pre_arrival = await pipeline.generate_pre_arrival()

    await pipeline.broadcast("phase", {
        "phase": 0,
        "title": "Pre-Arrival Intelligence",
        "status": "complete",
    })

    await asyncio.sleep(phase_delay)

    for phase_num in [1, 2, 3, 4]:
        phase = DEMO_SCRIPT[phase_num]
        pipeline.state.phase = phase_num

        await pipeline.broadcast("phase", {
            "phase": phase_num,
            "title": phase["title"],
            "status": "started",
        })

        for line in phase["lines"]:
            if line["delay"] > 0:
                await asyncio.sleep(line["delay"])

            entry = pipeline.add_transcript(
                speaker=line["speaker"],
                text=line["text"],
                phase=phase_num,
            )
            entry["intent_type"] = line.get("intent_type", "clinical_discussion")

            await pipeline.broadcast("transcript", entry)

            if line.get("intent_type") == "direct_query":
                await asyncio.sleep(2)
                await pipeline.query(line["text"], speaker=line["speaker"])

        await asyncio.sleep(2)

        if phase_num in [1, 2]:
            await pipeline.broadcast("phase", {
                "phase": phase_num,
                "title": phase["title"],
                "status": "processing",
            })

            result = await pipeline.process(phase=phase_num)

            await pipeline.broadcast("phase", {
                "phase": phase_num,
                "title": phase["title"],
                "status": "complete",
                "result_summary": result.get("status"),
            })
        elif phase_num == 3:
            await pipeline.broadcast("phase", {
                "phase": phase_num,
                "title": phase["title"],
                "status": "complete",
            })
        elif phase_num == 4:
            await pipeline.broadcast("phase", {
                "phase": phase_num,
                "title": phase["title"],
                "status": "processing",
            })

            result = await pipeline.process(phase=phase_num)

            await pipeline.broadcast("phase", {
                "phase": phase_num,
                "title": phase["title"],
                "status": "complete",
            })

        if phase_num < 4:
            await asyncio.sleep(phase_delay)

    await pipeline.broadcast("demo", {"status": "complete"})


async def run_demo_phase(pipeline: Pipeline, phase_num: int):
    """Run a single phase of the demo."""
    if phase_num == 0:
        await pipeline.broadcast("phase", {
            "phase": 0,
            "title": "Pre-Arrival Intelligence",
            "status": "started",
        })
        result = await pipeline.generate_pre_arrival()
        await pipeline.broadcast("phase", {
            "phase": 0,
            "title": "Pre-Arrival Intelligence",
            "status": "complete",
        })
        return {"status": "complete", "pre_arrival": result}

    if phase_num not in DEMO_SCRIPT:
        return {"error": f"Invalid phase: {phase_num}"}

    phase = DEMO_SCRIPT[phase_num]
    pipeline.state.phase = phase_num

    await pipeline.broadcast("phase", {
        "phase": phase_num,
        "title": phase["title"],
        "status": "started",
    })

    for line in phase["lines"]:
        if line["delay"] > 0:
            await asyncio.sleep(line["delay"])

        entry = pipeline.add_transcript(
            speaker=line["speaker"],
            text=line["text"],
            phase=phase_num,
        )
        entry["intent_type"] = line.get("intent_type", "clinical_discussion")
        await pipeline.broadcast("transcript", entry)

        if line.get("intent_type") == "direct_query":
            await asyncio.sleep(2)
            await pipeline.query(line["text"], speaker=line["speaker"])

    await asyncio.sleep(1)

    result = await pipeline.process(phase=phase_num)

    await pipeline.broadcast("phase", {
        "phase": phase_num,
        "title": phase["title"],
        "status": "complete",
    })

    return result
