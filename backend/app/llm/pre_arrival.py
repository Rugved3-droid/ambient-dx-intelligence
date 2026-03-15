"""Pre-arrival clinical intelligence via Claude Sonnet."""

from __future__ import annotations

from app.llm.clients import anthropic_client
from app.llm.parser import parse_json_response
from app.llm.prompts import PRE_ARRIVAL_SYSTEM_PROMPT


async def pre_arrival_intelligence(retrieved_data: list[dict]) -> dict:
    """Use Claude Sonnet to generate pre-arrival clinical intelligence."""
    data_text = "COMPLETE PATIENT EMR DATA:\n\n"
    for item in retrieved_data:
        data_text += f"[Source: {item['source']}] [Category: {item['category']}]\n{item['text']}\n\n"

    try:
        response = anthropic_client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=6000,
            system=PRE_ARRIVAL_SYSTEM_PROMPT,
            messages=[
                {
                    "role": "user",
                    "content": f"Analyze this patient's EMR data. The patient is acutely deteriorating (rapid response called). Generate the top 5 differential considerations with full evidence and clinical scores.\n\n{data_text}",
                }
            ],
        )
        return parse_json_response(response.content[0].text)
    except Exception as e:
        return {"error": str(e), "differentials": [], "safety_flags": []}
