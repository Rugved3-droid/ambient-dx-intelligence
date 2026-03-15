"""Intent recognition via GPT-4o-mini."""

from __future__ import annotations

from app.llm.clients import openai_client
from app.llm.parser import parse_json_response
from app.llm.prompts import INTENT_SYSTEM_PROMPT


async def recognize_intent(transcript: str) -> dict:
    """Use GPT-4o-mini to extract clinical intents from transcript."""
    try:
        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": INTENT_SYSTEM_PROMPT},
                {"role": "user", "content": f"Analyze this clinical conversation transcript:\n\n{transcript}"},
            ],
            temperature=0.1,
            max_tokens=1500,
        )
        return parse_json_response(response.choices[0].message.content)
    except Exception as e:
        return {"error": str(e), "has_clinical_intent": False, "intents": []}
