"""RAG Engine — smart retrieval from ChromaDB based on clinical intents."""

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
}

# Categories that should ALWAYS be retrieved for safety cross-referencing
SAFETY_ALWAYS_RETRIEVE = ["allergies", "problems", "medications"]


class RAGEngine:
    def __init__(self, patient_manager: PatientDataManager):
        self.pm = patient_manager

    def retrieve(
        self,
        query: str,
        n_results: int = 10,
        categories: list[str] | None = None,
        include_safety: bool = True,
    ) -> list[dict]:
        """Retrieve relevant patient data chunks.

        Args:
            query: The clinical question or search query
            n_results: Max results to return
            categories: Specific categories to filter by
            include_safety: Always include safety-critical data (allergies, problems, meds)
        """
        if not self.pm.collection:
            return []

        # Determine which categories to query
        target_categories = set()
        if categories:
            target_categories.update(categories)

        # Smart mapping: look for clinical concepts in the query
        query_lower = query.lower()
        for concept, cats in CONCEPT_CATEGORY_MAP.items():
            if concept in query_lower:
                target_categories.update(cats)

        # Always include safety categories
        if include_safety:
            target_categories.update(SAFETY_ALWAYS_RETRIEVE)

        # If still no categories, don't filter
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
            # Fallback: query without filter
            results = self.pm.collection.query(
                query_texts=[query],
                n_results=min(n_results, self.pm.collection.count()),
            )

        # Format results
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
                    "relevance_score": 1 - (dist or 0),  # Convert distance to similarity
                })

        return retrieved

    def retrieve_for_safety(self) -> list[dict]:
        """Retrieve ALL safety-critical data — medications, allergies, problem list, and relevant notes."""
        if not self.pm.collection:
            return []

        # Get all safety-critical chunks
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

    def retrieve_for_intent(self, intent: dict) -> list[dict]:
        """Retrieve data based on a structured clinical intent."""
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

        return self.retrieve(
            query=query,
            n_results=15,
            categories=list(categories),
            include_safety=True,
        )
