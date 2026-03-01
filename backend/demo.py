"""Demo Mode — 3-phase scripted rapid response scenario."""

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pipeline import Pipeline

DEMO_SCRIPT = {
    1: {
        "title": "Rapid Response Called",
        "lines": [
            {
                "speaker": "Nurse (RN Torres)",
                "text": "Rapid response room 412. BP dropped to 78 over 40, heart rate 122. He was hemodynamically stable an hour ago. He's on a heparin drip.",
                "delay": 0,
            },
            {
                "speaker": "Resident (Dr. Zhao)",
                "text": "Okay what's he in for? When did this start?",
                "delay": 4,
            },
            {
                "speaker": "Nurse (RN Torres)",
                "text": "Post-op day 6, right knee replacement. He was doing great, supposed to go home tomorrow. Around 1 PM he got diaphoretic and lightheaded, BP started trending down. We gave a fluid bolus but he's not responding.",
                "delay": 3,
            },
        ],
    },
    2: {
        "title": "GI Bleed Discussion",
        "lines": [
            {
                "speaker": "Resident (Dr. Zhao)",
                "text": "Could this be a GI bleed? He's on heparin. Look at that hemoglobin, it went from 11.4 to 8.2 overnight.",
                "delay": 2,
            },
            {
                "speaker": "Senior (Dr. Patel)",
                "text": "Was a stool guaiac done?",
                "delay": 4,
            },
            {
                "speaker": "Resident (Dr. Zhao)",
                "text": "Doesn't look like it. But the nurse noted dark stool this morning. And the BUN jumped from 18 to 34.",
                "delay": 3,
            },
        ],
    },
    3: {
        "title": "PE Discussion + HIT Catch",
        "lines": [
            {
                "speaker": "Senior (Dr. Patel)",
                "text": "Wait, what about PE? He had knee surgery last week. That's a major VTE risk factor.",
                "delay": 2,
            },
            {
                "speaker": "Resident (Dr. Zhao)",
                "text": "But he's already on heparin. Can you get a PE on heparin?",
                "delay": 4,
            },
            {
                "speaker": "Senior (Dr. Patel)",
                "text": "You can. Especially if the dose is subtherapeutic or if there's something else going on. Check his Wells score. Also, what are his platelets doing?",
                "delay": 3,
            },
        ],
    },
}


async def run_demo(pipeline: Pipeline, phase_delay: float = 8.0):
    """Run the full 3-phase demo scenario.

    Args:
        pipeline: The pipeline instance
        phase_delay: Seconds to wait between phases for processing
    """
    for phase_num in [1, 2, 3]:
        phase = DEMO_SCRIPT[phase_num]
        pipeline.state.phase = phase_num

        # Broadcast phase start
        await pipeline.broadcast("phase", {
            "phase": phase_num,
            "title": phase["title"],
            "status": "started",
        })

        # Feed transcript lines with delays
        for line in phase["lines"]:
            if line["delay"] > 0:
                await asyncio.sleep(line["delay"])

            entry = pipeline.add_transcript(
                speaker=line["speaker"],
                text=line["text"],
                phase=phase_num,
            )

            # Broadcast each transcript line
            await pipeline.broadcast("transcript", entry)

        # Wait a moment for the transcript to settle
        await asyncio.sleep(2)

        # Trigger processing for this phase
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

        # Delay between phases
        if phase_num < 3:
            await asyncio.sleep(phase_delay)

    await pipeline.broadcast("demo", {"status": "complete"})


async def run_demo_phase(pipeline: Pipeline, phase_num: int):
    """Run a single phase of the demo."""
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
        await pipeline.broadcast("transcript", entry)

    await asyncio.sleep(1)

    result = await pipeline.process(phase=phase_num)

    await pipeline.broadcast("phase", {
        "phase": phase_num,
        "title": phase["title"],
        "status": "complete",
    })

    return result
