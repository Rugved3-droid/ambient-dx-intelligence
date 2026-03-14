"""Pipeline Orchestrator — chains transcript → intent → RAG → reasoning → WebSocket broadcast."""

from __future__ import annotations

import asyncio
import json
import time
from dataclasses import dataclass, field

from llm_interface import recognize_intent, diagnostic_reasoning, safety_crossref, quick_answer
from rag_engine import RAGEngine
from patient_data import PatientDataManager
from cached_responses import CACHED_RESPONSES


@dataclass
class PipelineState:
    """Tracks the full state of the diagnostic pipeline."""
    transcript_buffer: list[dict] = field(default_factory=list)
    current_intents: dict = field(default_factory=dict)
    retrieved_data: list[dict] = field(default_factory=list)
    diagnostic_result: dict = field(default_factory=dict)
    safety_result: dict = field(default_factory=dict)
    phase: int = 0
    processing: bool = False
    last_processed: float = 0
    use_cache: bool = False


class Pipeline:
    def __init__(self, use_cache: bool = False):
        self.pm = PatientDataManager()
        self.pm.initialize()
        self.rag = RAGEngine(self.pm)
        self.state = PipelineState(use_cache=use_cache)
        self.broadcast_callback = None  # Set by main.py

    def set_broadcast_callback(self, cb):
        self.broadcast_callback = cb

    async def broadcast(self, event_type: str, data: dict):
        if self.broadcast_callback:
            await self.broadcast_callback(event_type, data)

    def add_transcript(self, speaker: str, text: str, phase: int = 0):
        entry = {
            "speaker": speaker,
            "text": text,
            "timestamp": time.time(),
            "phase": phase,
        }
        self.state.transcript_buffer.append(entry)
        return entry

    def get_rolling_transcript(self, window_seconds: int = 90) -> str:
        """Get transcript text from the last N seconds."""
        cutoff = time.time() - window_seconds
        recent = [e for e in self.state.transcript_buffer if e["timestamp"] >= cutoff]
        if not recent:
            recent = self.state.transcript_buffer[-10:]  # fallback to last 10 entries
        return "\n".join(f"{e['speaker']}: {e['text']}" for e in recent)

    async def process(self, phase: int | None = None) -> dict:
        """Run the full pipeline: intent → RAG → reasoning + safety."""
        if self.state.processing:
            return {"status": "already_processing"}

        self.state.processing = True
        current_phase = phase if phase is not None else self.state.phase

        try:
            # Check cache first
            if self.state.use_cache and current_phase in CACHED_RESPONSES:
                cached = CACHED_RESPONSES[current_phase]
                self.state.current_intents = cached.get("intents", {})
                self.state.diagnostic_result = cached.get("diagnostic", {})
                self.state.safety_result = cached.get("safety", {})
                self.state.last_processed = time.time()

                await self.broadcast("intents", self.state.current_intents)
                await self.broadcast("diagnostic", self.state.diagnostic_result)
                if cached.get("safety", {}).get("safety_alerts"):
                    await self.broadcast("safety_alert", self.state.safety_result)

                return {
                    "status": "complete_cached",
                    "phase": current_phase,
                    "intents": self.state.current_intents,
                    "diagnostic": self.state.diagnostic_result,
                    "safety": self.state.safety_result,
                }

            # Step 1: Get rolling transcript
            transcript = self.get_rolling_transcript()
            if not transcript.strip():
                return {"status": "no_transcript"}

            # Step 2: Intent recognition (GPT-4o-mini)
            await self.broadcast("status", {"stage": "intent_recognition", "phase": current_phase})
            intents = await recognize_intent(transcript)
            self.state.current_intents = intents
            await self.broadcast("intents", intents)

            # Step 3: RAG retrieval
            await self.broadcast("status", {"stage": "data_retrieval", "phase": current_phase})
            all_retrieved = []

            if intents.get("intents"):
                for intent in intents["intents"]:
                    retrieved = self.rag.retrieve_for_intent(intent)
                    all_retrieved.extend(retrieved)

            # Deduplicate by source
            seen = set()
            unique_retrieved = []
            for item in all_retrieved:
                key = item["source"]
                if key not in seen:
                    seen.add(key)
                    unique_retrieved.append(item)

            self.state.retrieved_data = unique_retrieved

            # Step 4: Diagnostic reasoning + Safety cross-ref (parallel)
            await self.broadcast("status", {"stage": "diagnostic_reasoning", "phase": current_phase})

            # Build clinical question from intents
            questions = []
            for intent in intents.get("intents", []):
                if intent.get("diagnostic_question"):
                    questions.append(intent["diagnostic_question"])
                elif intent.get("summary"):
                    questions.append(intent["summary"])

            clinical_question = " AND ".join(questions) if questions else "Assess current clinical situation"

            # Run diagnostic reasoning and safety cross-ref in parallel
            safety_data = self.rag.retrieve_for_safety()

            diagnostic_task = diagnostic_reasoning(clinical_question, unique_retrieved)
            safety_task = safety_crossref(safety_data)

            diag_result, safety_result = await asyncio.gather(diagnostic_task, safety_task)

            self.state.diagnostic_result = diag_result
            self.state.safety_result = safety_result
            self.state.last_processed = time.time()

            # Broadcast results
            await self.broadcast("diagnostic", diag_result)
            if safety_result.get("safety_alerts"):
                await self.broadcast("safety_alert", safety_result)

            await self.broadcast("status", {"stage": "complete", "phase": current_phase})

            return {
                "status": "complete",
                "phase": current_phase,
                "intents": intents,
                "diagnostic": diag_result,
                "safety": safety_result,
            }

        except Exception as e:
            await self.broadcast("error", {"message": str(e)})
            return {"status": "error", "error": str(e)}
        finally:
            self.state.processing = False

    async def query(self, question: str, speaker: str = "Query") -> dict:
        """Fast Q&A — single GPT-4o-mini call for quick answers (~3-5 sec)."""
        if self.state.processing:
            return {"status": "already_processing"}

        self.state.processing = True

        try:
            # Add the query to transcript
            entry = self.add_transcript(speaker, question, phase=0)
            await self.broadcast("transcript", entry)

            # RAG retrieval — broad search
            await self.broadcast("status", {"stage": "data_retrieval"})
            retrieved = self.rag.retrieve(
                question, n_results=12,
                categories=["vitals", "labs", "medications", "allergies", "problems", "notes", "imaging", "history"],
                include_safety=True,
            )
            self.state.retrieved_data = retrieved

            # Single fast LLM call — GPT-4o-mini
            await self.broadcast("status", {"stage": "generating_answer"})
            answer_result = await quick_answer(question, retrieved)

            self.state.last_processed = time.time()

            # Broadcast the answer
            await self.broadcast("answer", {
                "question": question,
                "answer": answer_result.get("answer", "Unable to generate answer."),
                "citations": answer_result.get("citations", []),
                "confidence": answer_result.get("confidence", "low"),
                "follow_up_suggestions": answer_result.get("follow_up_suggestions", []),
            })

            await self.broadcast("status", {"stage": "complete"})

            return {
                "status": "complete",
                "answer": answer_result,
            }

        except Exception as e:
            await self.broadcast("error", {"message": str(e)})
            return {"status": "error", "error": str(e)}
        finally:
            self.state.processing = False

    def get_state(self) -> dict:
        return {
            "transcript_count": len(self.state.transcript_buffer),
            "phase": self.state.phase,
            "processing": self.state.processing,
            "has_intents": bool(self.state.current_intents),
            "has_diagnostic": bool(self.state.diagnostic_result),
            "has_safety_alert": bool(
                self.state.safety_result.get("safety_alerts")
            ),
            "last_processed": self.state.last_processed,
        }
