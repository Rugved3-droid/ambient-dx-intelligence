"""Quick clinical Q&A via GPT-4o."""

from __future__ import annotations

from app.llm.clients import openai_client
from app.llm.parser import parse_json_response
from app.llm.prompts import QUICK_ANSWER_SYSTEM_PROMPT


async def quick_answer(question: str, retrieved_data: list[dict]) -> dict:
    """Use GPT-4o for fast, accurate clinical Q&A."""
    data_text = "RETRIEVED PATIENT DATA:\n\n"
    for item in retrieved_data:
        data_text += f"[Source: {item['source']}] [Category: {item['category']}]\n{item['text']}\n\n"

    try:
        response = openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": QUICK_ANSWER_SYSTEM_PROMPT},
                {"role": "user", "content": f"CLINICAL QUESTION: {question}\n\n{data_text}"},
            ],
            temperature=0.1,
            max_tokens=2000,
        )
        return parse_json_response(response.choices[0].message.content)
    except Exception as e:
        return {"answer": f"Error generating answer: {e}", "citations": [], "confidence": "low"}
