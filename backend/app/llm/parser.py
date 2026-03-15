"""JSON parsing helpers for LLM responses."""

from __future__ import annotations

import json


def parse_json_response(text: str) -> dict:
    """Robustly parse JSON from LLM response, handling markdown fences."""
    text = text.strip()
    if text.startswith("```"):
        lines = text.split("\n")
        lines = [l for l in lines if not l.strip().startswith("```")]
        text = "\n".join(lines)
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        start = text.find("{")
        end = text.rfind("}") + 1
        if start >= 0 and end > start:
            return json.loads(text[start:end])
        return {"error": "Failed to parse JSON", "raw": text[:500]}
