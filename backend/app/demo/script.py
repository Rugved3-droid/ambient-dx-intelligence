"""Demo script — 4-phase scripted rapid response scenario data."""

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
