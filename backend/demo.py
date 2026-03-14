"""Demo Mode — 4-phase scripted rapid response scenario with voice queries."""

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pipeline import Pipeline

DEMO_SCRIPT = {
    1: {
        "title": "Rapid Response — Team Arrives",
        "lines": [
            {
                "speaker": "Nurse (RN Torres)",
                "text": "Rapid response room 412. BP dropped to 78 over 40, heart rate 122. He was stable an hour ago. He's on a heparin drip.",
                "delay": 0,
                "intent_type": "clinical_discussion",
            },
            {
                "speaker": "Resident (Dr. Zhao)",
                "text": "Okay what's he in for? When did this start?",
                "delay": 4,
                "intent_type": "clinical_discussion",
            },
            {
                "speaker": "Nurse (RN Torres)",
                "text": "Post-op day 6, right knee replacement. Was doing great, supposed to go home tomorrow. Around 1 PM he got diaphoretic and lightheaded.",
                "delay": 3,
                "intent_type": "clinical_discussion",
            },
        ],
    },
    2: {
        "title": "GI Bleed Discussion",
        "lines": [
            {
                "speaker": "Resident (Dr. Zhao)",
                "text": "Could this be a GI bleed? Look at that hemoglobin drop.",
                "delay": 2,
                "intent_type": "clinical_discussion",
            },
            {
                "speaker": "Senior (Dr. Patel)",
                "text": "Was a stool guaiac done?",
                "delay": 4,
                "intent_type": "clinical_discussion",
            },
            {
                "speaker": "Resident (Dr. Zhao)",
                "text": "Doesn't look like it. Nurse noted dark stool this morning. BUN jumped from 18 to 34.",
                "delay": 3,
                "intent_type": "clinical_discussion",
            },
        ],
    },
    3: {
        "title": "PE Discussion + Voice Queries",
        "lines": [
            {
                "speaker": "Senior (Dr. Patel)",
                "text": "What about PE? He had surgery last week.",
                "delay": 2,
                "intent_type": "clinical_discussion",
            },
            {
                "speaker": "Resident (Dr. Zhao)",
                "text": "But he's on heparin.",
                "delay": 3,
                "intent_type": "clinical_discussion",
            },
            {
                "speaker": "Code Leader (Dr. Patel)",
                "text": "What's the Wells score for PE on this patient?",
                "delay": 4,
                "intent_type": "direct_query",
            },
            {
                "speaker": "Senior (Dr. Patel)",
                "text": "What are his platelets doing?",
                "delay": 8,
                "intent_type": "clinical_discussion",
            },
            {
                "speaker": "Code Leader (Dr. Patel)",
                "text": "Show me the platelet trend.",
                "delay": 3,
                "intent_type": "direct_query",
            },
        ],
    },
    4: {
        "title": "HIT Safety Alert",
        "lines": [
            {
                "speaker": "Resident (Dr. Zhao)",
                "text": "Wait — he had HIT before? That wasn't flagged in his allergies.",
                "delay": 6,
                "intent_type": "clinical_discussion",
            },
        ],
    },
}


async def run_demo(pipeline: Pipeline, phase_delay: float = 8.0):
    """Run the full 4-phase demo scenario.

    Phase 0: Pre-arrival intelligence (auto-generated before conversation)
    Phase 1-4: Scripted conversation with processing
    """
    # Phase 0: Pre-arrival intelligence
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

    # Wait before conversation starts
    await asyncio.sleep(phase_delay)

    for phase_num in [1, 2, 3, 4]:
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
            entry["intent_type"] = line.get("intent_type", "clinical_discussion")

            # Broadcast each transcript line
            await pipeline.broadcast("transcript", entry)

            # If it's a direct query, process it as a voice query
            if line.get("intent_type") == "direct_query":
                await asyncio.sleep(2)  # Natural delay before response
                await pipeline.query(line["text"], speaker=line["speaker"])

        # Wait a moment for the transcript to settle
        await asyncio.sleep(2)

        # Trigger processing for conversation phases
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
            # Phase 3 uses voice queries (already processed above)
            await pipeline.broadcast("phase", {
                "phase": phase_num,
                "title": phase["title"],
                "status": "complete",
            })
        elif phase_num == 4:
            # Phase 4: Safety alert fires autonomously
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

        # Delay between phases
        if phase_num < 4:
            await asyncio.sleep(phase_delay)

    await pipeline.broadcast("demo", {"status": "complete"})


async def run_demo_phase(pipeline: Pipeline, phase_num: int):
    """Run a single phase of the demo."""
    if phase_num == 0:
        # Pre-arrival intelligence
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

        # Handle direct queries
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
