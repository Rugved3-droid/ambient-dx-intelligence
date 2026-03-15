"""Medication safety cross-referencing via Claude Sonnet."""

from __future__ import annotations

from app.llm.clients import anthropic_client
from app.llm.parser import parse_json_response
from app.llm.prompts import SAFETY_SYSTEM_PROMPT


async def safety_crossref(retrieved_data: list[dict]) -> dict:
    """Use Claude Sonnet for medication safety cross-referencing."""
    data_text = "COMPLETE PATIENT DATA FOR SAFETY REVIEW:\n\n"
    for item in retrieved_data:
        data_text += f"[Source: {item['source']}] [Category: {item['category']}]\n{item['text']}\n\n"

    try:
        response = anthropic_client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2000,
            system=SAFETY_SYSTEM_PROMPT,
            messages=[
                {
                    "role": "user",
                    "content": f"Review all current medications against this patient's complete history, allergies, and prior adverse reactions:\n\n{data_text}",
                }
            ],
        )
        return parse_json_response(response.content[0].text)
    except Exception as e:
        return {"error": str(e), "safety_alerts": [], "no_alerts": True}
