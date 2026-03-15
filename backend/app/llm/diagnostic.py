"""Diagnostic reasoning via Claude Sonnet."""

from __future__ import annotations

from app.llm.clients import anthropic_client
from app.llm.parser import parse_json_response
from app.llm.prompts import DIAGNOSTIC_SYSTEM_PROMPT


async def diagnostic_reasoning(clinical_question: str, retrieved_data: list[dict]) -> dict:
    """Use Claude Sonnet for diagnostic reasoning."""
    data_text = "RETRIEVED PATIENT DATA:\n\n"
    for item in retrieved_data:
        data_text += f"[Source: {item['source']}] [Category: {item['category']}]\n{item['text']}\n\n"

    try:
        response = anthropic_client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4000,
            system=DIAGNOSTIC_SYSTEM_PROMPT,
            messages=[
                {
                    "role": "user",
                    "content": f"CLINICAL QUESTION: {clinical_question}\n\n{data_text}",
                }
            ],
        )
        return parse_json_response(response.content[0].text)
    except Exception as e:
        return {"error": str(e), "critical_alerts": [], "differential_diagnoses": []}
