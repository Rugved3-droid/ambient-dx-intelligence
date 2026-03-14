"""LLM Interface — GPT-4o-mini for intent recognition, Claude Sonnet for diagnostic reasoning."""

from __future__ import annotations

import json
import os
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

import anthropic
import openai

openai_client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
anthropic_client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

# ─── System Prompts ───

INTENT_SYSTEM_PROMPT = """You are a clinical intent recognition engine. You analyze transcripts of clinical conversations and extract structured clinical intents.

When analyzing the transcript, classify each segment as one of:
1. "clinical_discussion" — team members talking to each other about the patient
2. "direct_query" — someone asking a specific question that expects a data-driven answer (e.g. "What's the Wells score?", "Show me the platelet trend", "What meds is he on?")
3. "administrative" — logistics, non-clinical talk (ignore)

For direct_query, extract:
- The specific question being asked
- What data type is needed (score calculation, lab value, medication info, imaging, history)
- The urgency of the query

For clinical_discussion, extract:
- Diagnostic questions being asked or implied
- What patient data would help answer them
- Action items being discussed
- Urgency level

Respond ONLY with valid JSON:
{
  "has_clinical_intent": true/false,
  "intent_type": "clinical_discussion|direct_query|mixed",
  "intents": [{
    "type": "diagnostic_query|data_request|action_item|differential_diagnosis|direct_query",
    "summary": "Brief description",
    "diagnostic_question": "The core clinical question",
    "query_text": "The exact question if direct_query type",
    "query_data_type": "score_calculation|lab_value|medication_info|imaging|history|trend",
    "data_needed": [{"category": "labs|vitals|medications|notes|imaging|history|scores", "specifics": "..."}],
    "differentials_mentioned": ["list of diagnoses"],
    "urgency": "critical|high|routine",
    "clinical_context": "Why this matters"
  }],
  "action_items": [{"action": "...", "priority": "stat|urgent|routine", "status": "discussed|ordered"}]
}

IMPORTANT: Extract IMPLICIT diagnostic questions. If someone says "they're on heparin and platelets are dropping," the implicit question is "could this be HIT?" Always include medication-related data needs when hemodynamic instability is discussed."""

DIAGNOSTIC_SYSTEM_PROMPT = """You are a diagnostic reasoning engine. You receive a clinical question and relevant patient data retrieved from the EMR. Provide grounded, cited diagnostic reasoning.

CRITICAL RULES:
- EVERY factual claim must cite its specific EMR source and timestamp
- NEVER state a value without citing where it came from
- If data wasn't provided, say "Not available in retrieved records"
- Cross-reference current medications with historical diagnoses
- When hemoglobin drops, calculate rate of decline
- When platelets drop, calculate percentage decline relative to heparin exposure
- Flag medication-disease interactions as critical alerts

Respond ONLY with valid JSON:
{
  "patient_summary": {"one_liner": "...", "active_situation": "..."},
  "critical_alerts": [{"severity": "critical|warning", "finding": "...", "evidence": "...", "source": "...", "action_required": "..."}],
  "differential_diagnoses": [{"diagnosis": "...", "likelihood": "high|moderate|low", "evidence_for": [{"finding": "...", "source": "...", "strength": "strong|moderate|weak"}], "evidence_against": [{"finding": "...", "source": "...", "strength": "strong|moderate|weak"}], "data_gaps": ["..."], "recommended_workup": ["..."]}],
  "clinical_scores": [{"score_name": "...", "calculated_value": "...", "interpretation": "...", "components": [{"criterion": "...", "value": "...", "points": "...", "source": "..."}]}],
  "suggested_actions": [{"action": "...", "priority": "immediate|urgent|soon", "rationale": "..."}]
}"""

SAFETY_SYSTEM_PROMPT = """You are a medication safety cross-reference engine. Compare current medications against complete medical history, allergy list, and prior adverse reactions. LOW threshold for alerting — false positives are better than false negatives.

Look for: medications patient has documented adverse reactions to, contraindicated medications given history, dangerous drug interactions, inappropriate dosing for organ function.

Respond ONLY with JSON:
{
  "safety_alerts": [{"severity": "critical|warning", "type": "contraindication|allergy|interaction|dosing", "medication": "...", "historical_event": "...", "historical_source": "...", "current_source": "...", "risk": "...", "recommended_action": "..."}],
  "no_alerts": true/false
}"""


def _parse_json_response(text: str) -> dict:
    """Robustly parse JSON from LLM response, handling markdown fences."""
    text = text.strip()
    if text.startswith("```"):
        # Remove markdown code fences
        lines = text.split("\n")
        lines = [l for l in lines if not l.strip().startswith("```")]
        text = "\n".join(lines)
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        # Try to find JSON object in the text
        start = text.find("{")
        end = text.rfind("}") + 1
        if start >= 0 and end > start:
            return json.loads(text[start:end])
        return {"error": "Failed to parse JSON", "raw": text[:500]}


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
        return _parse_json_response(response.choices[0].message.content)
    except Exception as e:
        return {"error": str(e), "has_clinical_intent": False, "intents": []}


async def diagnostic_reasoning(clinical_question: str, retrieved_data: list[dict]) -> dict:
    """Use Claude Sonnet for diagnostic reasoning."""
    # Format retrieved data
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
        return _parse_json_response(response.content[0].text)
    except Exception as e:
        return {"error": str(e), "critical_alerts": [], "differential_diagnoses": []}


QUICK_ANSWER_SYSTEM_PROMPT = """You are a clinical decision support AI. A clinician has asked you a question about a patient. You have access to the patient's EMR data retrieved via semantic search.

CRITICAL RULES:
- Answer the question DIRECTLY and conversationally, but ground every claim in patient data
- Use inline citations in the format [Source: XYZ] after each factual claim
- If data isn't available for something, say so — NEVER fabricate values
- Keep the answer focused and concise (3-8 sentences for simple questions, more for complex)
- Highlight critical safety concerns prominently
- When discussing lab trends, include actual values and dates
- If the question touches on medication safety, cross-reference allergies and history
- Calculate clinical scores when asked (Wells, HEART, SOFA, 4Ts, GRACE, etc.) using available data

Respond ONLY with valid JSON:
{
  "answer": "Your natural language answer with [Source: ...] citations inline...",
  "citations": [{"source": "...", "category": "...", "relevant_text": "brief excerpt"}],
  "confidence": "high|moderate|low",
  "follow_up_suggestions": ["Optional follow-up questions the clinician might want to ask"]
}"""


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
        return _parse_json_response(response.choices[0].message.content)
    except Exception as e:
        return {"answer": f"Error generating answer: {e}", "citations": [], "confidence": "low"}


PRE_ARRIVAL_SYSTEM_PROMPT = """You are a clinical pre-arrival intelligence engine. Given a patient's current EMR data showing acute deterioration, generate the top 5 most likely differential diagnoses with supporting evidence from the chart data.

For each differential:
- Name the condition
- Rate evidence strength: "Strong" / "Moderate" / "Weak" (NEVER use percentages or probabilities)
- List supporting findings with exact values and EMR source citations
- Calculate any relevant clinical scores with full component breakdown
- List data gaps that would help confirm or exclude

Rules:
- EVERY value must cite its source (which lab panel, which vital sign reading, which note, with timestamp)
- Show evidence STRENGTH not likelihood PERCENTAGE
- Include at least one differential the team might not immediately consider
- Note any critical medication-history interactions as a separate safety flag

Respond ONLY with valid JSON:
{
  "header": "PRE-ARRIVAL CLINICAL INTELLIGENCE — Generated from EMR data",
  "differentials": [{
    "rank": 1,
    "name": "Condition name",
    "evidence_strength": "Strong|Moderate|Weak",
    "supporting_count": 4,
    "evidence": [{"finding": "...", "source": "...", "timestamp": "..."}],
    "clinical_score": {"name": "...", "value": "...", "interpretation": "...", "components": [{"criterion": "...", "met": true, "points": 1.5, "evidence": "...", "source": "..."}]} | null,
    "data_gaps": ["..."]
  }],
  "safety_flags": [{"severity": "critical|warning", "flag": "...", "evidence": "...", "action": "..."}]
}"""


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
        return _parse_json_response(response.content[0].text)
    except Exception as e:
        return {"error": str(e), "differentials": [], "safety_flags": []}


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
        return _parse_json_response(response.content[0].text)
    except Exception as e:
        return {"error": str(e), "safety_alerts": [], "no_alerts": True}
