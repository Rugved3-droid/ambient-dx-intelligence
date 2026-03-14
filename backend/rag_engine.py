"""RAG Engine — smart retrieval from ChromaDB or IRIS based on clinical intents."""

from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from patient_data import PatientDataManager


# Map clinical concepts to data categories for targeted retrieval
CONCEPT_CATEGORY_MAP = {
    "gi bleed": ["labs", "medications", "vitals", "notes"],
    "gastrointestinal": ["labs", "medications", "notes"],
    "hemorrhage": ["labs", "medications", "vitals"],
    "bleeding": ["labs", "medications", "vitals", "notes"],
    "hemoglobin": ["labs"],
    "anemia": ["labs"],
    "pe": ["labs", "vitals", "medications", "notes", "history"],
    "pulmonary embolism": ["labs", "vitals", "medications", "notes", "history"],
    "dvt": ["labs", "medications", "notes", "history", "imaging"],
    "vte": ["labs", "medications", "notes", "history"],
    "hit": ["labs", "medications", "allergies", "notes", "problems"],
    "heparin": ["medications", "allergies", "notes", "problems"],
    "thrombocytopenia": ["labs", "medications", "allergies", "notes"],
    "platelets": ["labs", "medications", "allergies"],
    "hypotension": ["vitals", "labs", "medications"],
    "tachycardia": ["vitals", "labs"],
    "sepsis": ["vitals", "labs", "medications", "notes"],
    "anticoagulation": ["medications", "allergies", "labs", "notes"],
    "wells": ["vitals", "history", "notes", "labs"],
    "sofa": ["vitals", "labs"],
    "vital": ["vitals", "labs"],
    "blood pressure": ["vitals"],
    "heart rate": ["vitals"],
    "temperature": ["vitals"],
    "spo2": ["vitals"],
    "oxygen": ["vitals"],
    "lab": ["labs"],
    "score": ["labs", "vitals", "notes", "history", "medications"],
    "heart score": ["labs", "vitals", "notes", "history", "medications"],
    "grace": ["labs", "vitals", "notes", "history", "medications"],
    "trend": ["labs", "vitals"],
    "imaging": ["imaging"],
    "xray": ["imaging"],
    "ct": ["imaging"],
    "note": ["notes"],
    "history": ["history", "notes"],
    "medication": ["medications"],
    "allergy": ["allergies"],
    "diagnosis": ["problems", "notes"],
    "surgery": ["notes", "imaging"],
    "post.op": ["vitals", "labs", "medications", "notes"],
}

# Categories that should ALWAYS be retrieved for safety cross-referencing
SAFETY_ALWAYS_RETRIEVE = ["allergies", "problems", "medications"]


class RAGEngine:
    def __init__(self, patient_manager: PatientDataManager, use_iris: bool = False):
        self.pm = patient_manager
        self.use_iris = use_iris

    # ─── Category Resolution (shared by both backends) ───

    def _resolve_categories(
        self, query: str, categories: list[str] | None = None, include_safety: bool = True
    ) -> set[str]:
        target = set(categories or [])
        query_lower = query.lower()
        for concept, cats in CONCEPT_CATEGORY_MAP.items():
            if concept in query_lower:
                target.update(cats)
        if include_safety:
            target.update(SAFETY_ALWAYS_RETRIEVE)
        return target

    # ─── Main Entry Points ───

    def retrieve(
        self,
        query: str,
        n_results: int = 10,
        categories: list[str] | None = None,
        include_safety: bool = True,
    ) -> list[dict]:
        if self.use_iris:
            return self._retrieve_iris(query, n_results, categories, include_safety)
        return self._retrieve_chromadb(query, n_results, categories, include_safety)

    def retrieve_for_safety(self) -> list[dict]:
        if self.use_iris:
            return self._safety_iris()
        return self._safety_chromadb()

    def retrieve_for_intent(self, intent: dict) -> list[dict]:
        query_parts = []
        categories = set(SAFETY_ALWAYS_RETRIEVE)

        if intent.get("diagnostic_question"):
            query_parts.append(intent["diagnostic_question"])
        if intent.get("summary"):
            query_parts.append(intent["summary"])
        if intent.get("differentials_mentioned"):
            query_parts.extend(intent["differentials_mentioned"])
        if intent.get("data_needed"):
            for need in intent["data_needed"]:
                cat = need.get("category", "")
                if cat:
                    categories.add(cat)
                if need.get("specifics"):
                    query_parts.append(need["specifics"])

        query = " ".join(query_parts) if query_parts else "patient overview"
        return self.retrieve(query=query, n_results=15, categories=list(categories), include_safety=True)

    # ─── IRIS Hybrid Retrieval ───

    def _retrieve_iris(
        self, query: str, n_results: int, categories: list[str] | None, include_safety: bool
    ) -> list[dict]:
        from iris_db import (
            get_medications, get_allergies, get_problems,
            get_lab_trend, get_vitals_trend, get_heparin_status,
            get_critical_problems, get_recent_labs, PATIENT_ID,
        )
        from iris_vector_store import similarity_search

        target_cats = self._resolve_categories(query, categories, include_safety)
        results: list[dict] = []

        # 1) Structured SQL retrieval — exact clinical facts
        if "medications" in target_cats:
            results.extend(get_medications(PATIENT_ID))
        if "allergies" in target_cats:
            results.extend(get_allergies(PATIENT_ID))
        if "problems" in target_cats:
            results.extend(get_problems(PATIENT_ID))
            results.extend(get_critical_problems(PATIENT_ID))
        if "vitals" in target_cats:
            results.extend(get_vitals_trend(PATIENT_ID))
        if "labs" in target_cats:
            results.extend(get_recent_labs(PATIENT_ID))
            query_lower = query.lower()
            if "platelet" in query_lower or "hit" in query_lower or "thrombocytopenia" in query_lower:
                results.extend(get_lab_trend(PATIENT_ID, "platelets"))
            if "hemoglobin" in query_lower or "hgb" in query_lower or "bleed" in query_lower or "anemia" in query_lower:
                results.extend(get_lab_trend(PATIENT_ID, "hemoglobin"))

        # Heparin safety check on any query involving meds/anticoagulation/safety
        if any(kw in query.lower() for kw in ["heparin", "anticoag", "hit", "medication", "safety"]):
            results.extend(get_heparin_status(PATIENT_ID))

        # 2) IRIS vector search — narrative / note retrieval
        vector_cats = [c for c in target_cats if c in ("notes", "history", "imaging")]
        if not vector_cats:
            vector_cats = None
        vector_results = similarity_search(
            query, patient_id=PATIENT_ID, categories=vector_cats, top_k=n_results,
        )
        results.extend(vector_results)

        return self._deduplicate(results)

    def _safety_iris(self) -> list[dict]:
        from iris_db import (
            get_medications, get_allergies, get_problems,
            get_critical_problems, get_heparin_status, PATIENT_ID,
        )
        from iris_vector_store import similarity_search

        results: list[dict] = []
        results.extend(get_medications(PATIENT_ID))
        results.extend(get_allergies(PATIENT_ID))
        results.extend(get_problems(PATIENT_ID))
        results.extend(get_critical_problems(PATIENT_ID))
        results.extend(get_heparin_status(PATIENT_ID))

        note_results = similarity_search(
            "medication safety allergy contraindication adverse reaction",
            patient_id=PATIENT_ID,
            categories=["notes"],
            top_k=8,
        )
        results.extend(note_results)
        return self._deduplicate(results)

    # ─── ChromaDB Retrieval (original) ───

    def _retrieve_chromadb(
        self, query: str, n_results: int, categories: list[str] | None, include_safety: bool
    ) -> list[dict]:
        if not self.pm.collection:
            return []

        target_categories = self._resolve_categories(query, categories, include_safety)

        where_filter = None
        if target_categories:
            where_filter = {"category": {"$in": list(target_categories)}}

        try:
            results = self.pm.collection.query(
                query_texts=[query],
                n_results=min(n_results, self.pm.collection.count()),
                where=where_filter,
            )
        except Exception:
            results = self.pm.collection.query(
                query_texts=[query],
                n_results=min(n_results, self.pm.collection.count()),
            )

        retrieved = []
        if results and results["documents"]:
            for i, doc in enumerate(results["documents"][0]):
                meta = results["metadatas"][0][i] if results["metadatas"] else {}
                dist = results["distances"][0][i] if results["distances"] else None
                retrieved.append({
                    "text": doc,
                    "source": meta.get("source", "Unknown"),
                    "category": meta.get("category", "Unknown"),
                    "timestamp": meta.get("timestamp", ""),
                    "relevance_score": 1 - (dist or 0),
                })
        return retrieved

    def _safety_chromadb(self) -> list[dict]:
        if not self.pm.collection:
            return []
        all_chunks = self.pm.get_all_chunks()
        safety_chunks = [
            c for c in all_chunks
            if c["category"] in ["allergies", "problems", "medications", "notes"]
        ]
        return [
            {
                "text": c["text"],
                "source": c["source"],
                "category": c["category"],
                "timestamp": c["timestamp"],
                "relevance_score": 1.0,
            }
            for c in safety_chunks
        ]

    # ─── Shared Utilities ───

    @staticmethod
    def _deduplicate(results: list[dict]) -> list[dict]:
        seen = set()
        unique = []
        for item in results:
            key = item["source"]
            if key not in seen:
                seen.add(key)
                unique.append(item)
        return unique
