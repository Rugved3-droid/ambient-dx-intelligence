"""Patient Data Manager — loads patient JSON, chunks it, and loads into ChromaDB."""

import json
import os
from pathlib import Path

import chromadb
from chromadb.config import Settings

DATA_DIR = Path(__file__).parent / "data"
PATIENT_FILE = DATA_DIR / "patient_robert_chen.json"


def load_patient_json() -> dict:
    with open(PATIENT_FILE) as f:
        return json.load(f)


def chunk_patient_data(patient_data: dict) -> list[dict]:
    """Break patient record into semantically meaningful chunks with metadata."""
    p = patient_data["patient"]
    chunks = []

    # Demographics
    demo = p["demographics"]
    chunks.append({
        "id": "demographics",
        "text": (
            f"Patient: {demo['name']}, {demo['age']}yo {demo['sex']}. "
            f"MRN: {demo['mrn']}. Room {demo['room']}{demo['bed']}. "
            f"Admitted {demo['admission_date']}. Attending: {demo['attending']}. "
            f"Code status: {demo['code_status']}. "
            f"Weight {demo['weight_kg']}kg, Height {demo['height_cm']}cm, BMI {demo['bmi']}."
        ),
        "category": "demographics",
        "source": "Demographics",
        "timestamp": demo["admission_date"],
    })

    # Allergies — each as separate chunk (critical for safety)
    for i, allergy in enumerate(p["allergies"]):
        text = f"ALLERGY: {allergy['allergen']} — Reaction: {allergy['reaction']}. Severity: {allergy['severity']}."
        if allergy.get("documented_date"):
            text += f" Documented: {allergy['documented_date']}."
        if allergy.get("source"):
            text += f" Source: {allergy['source']}."
        chunks.append({
            "id": f"allergy_{i}",
            "text": text,
            "category": "allergies",
            "source": f"Allergy List",
            "timestamp": allergy.get("documented_date", demo["admission_date"]),
        })

    # Problem list
    problems_text = "PROBLEM LIST:\n"
    for prob in p["problem_list"]:
        line = f"- {prob['problem']} — Status: {prob['status']}"
        if prob.get("critical_flag"):
            line += " *** CRITICAL FLAG ***"
        problems_text += line + "\n"
    chunks.append({
        "id": "problem_list",
        "text": problems_text,
        "category": "problems",
        "source": "Problem List",
        "timestamp": demo["admission_date"],
    })

    # Each medication as separate chunk
    for i, med in enumerate(p["current_medications"]):
        text = (
            f"MEDICATION: {med['name']} {med['dose']} {med['route']} {med['frequency']}. "
            f"Start: {med['start_date']}. Indication: {med['indication']}. "
            f"Status: {med['status']}."
        )
        if med.get("ordered_by"):
            text += f" Ordered by: {med['ordered_by']}."
        if med.get("notes"):
            text += f" Notes: {med['notes']}"
        chunks.append({
            "id": f"medication_{i}_{med['name'].lower().replace(' ', '_')}",
            "text": text,
            "category": "medications",
            "source": f"Medication List — {med['name']}",
            "timestamp": med["start_date"],
        })

    # Medication list combined (for overview retrieval)
    med_summary = "CURRENT MEDICATIONS:\n"
    for med in p["current_medications"]:
        med_summary += f"- {med['name']} {med['dose']} {med['route']} {med['frequency']} ({med['status']})\n"
    chunks.append({
        "id": "medications_summary",
        "text": med_summary,
        "category": "medications",
        "source": "Medication List — Summary",
        "timestamp": demo["admission_date"],
    })

    # Labs — each timepoint as separate chunk
    for tp in p["labs"]["timestamps"]:
        text = f"LAB RESULTS — {tp['label']} ({tp['timestamp']}):\n"
        for name, val in tp["results"].items():
            line = f"  {name}: {val['value']} {val['unit']} (ref {val['ref_range']}) [{val['flag']}]"
            if val.get("note"):
                line += f" — {val['note']}"
            text += line + "\n"
        chunks.append({
            "id": f"labs_{tp['label'].replace(' ', '_').replace('#', '').lower()}",
            "text": text,
            "category": "labs",
            "source": f"Labs — {tp['label']}",
            "timestamp": tp["timestamp"],
        })

    # Lab trends — hemoglobin
    hgb_trend = "HEMOGLOBIN TREND:\n"
    for tp in p["labs"]["timestamps"]:
        if "hemoglobin" in tp["results"]:
            hgb = tp["results"]["hemoglobin"]
            hgb_trend += f"  {tp['label']}: {hgb['value']} {hgb['unit']} [{hgb['flag']}]\n"
    hgb_trend += "Rate of decline: 12.1 → 8.2 g/dL over 4 days (3.9 g/dL drop, accelerating: 1.9 g/dL drop in last 24h)"
    chunks.append({
        "id": "lab_trend_hemoglobin",
        "text": hgb_trend,
        "category": "labs",
        "source": "Lab Trend — Hemoglobin",
        "timestamp": p["labs"]["timestamps"][-1]["timestamp"],
    })

    # Lab trends — platelets
    plt_trend = "PLATELET TREND:\n"
    for tp in p["labs"]["timestamps"]:
        if "platelets" in tp["results"]:
            plt = tp["results"]["platelets"]
            plt_trend += f"  {tp['label']}: {plt['value']} {plt['unit']} [{plt['flag']}]\n"
    plt_trend += (
        "Platelet decline: 220 → 89 K/uL (59.5% decline from admission baseline). "
        "Heparin started POD#1 (2026-03-10). "
        "Decline pattern consistent with HIT timeline (onset day 4-5 of heparin exposure). "
        "Current day of heparin exposure: Day 4."
    )
    chunks.append({
        "id": "lab_trend_platelets",
        "text": plt_trend,
        "category": "labs",
        "source": "Lab Trend — Platelets",
        "timestamp": p["labs"]["timestamps"][-1]["timestamp"],
    })

    # Vitals trend
    vitals_text = "VITALS TREND — POD#6 (Today):\n"
    for v in p["vitals"]["trend"]:
        vitals_text += (
            f"  {v['label']}: BP {v['bp_systolic']}/{v['bp_diastolic']}, "
            f"HR {v['heart_rate']}, RR {v['resp_rate']}, "
            f"SpO2 {v['spo2']}%, T {v['temp']}°C\n"
        )
    vitals_text += "TREND: Progressive hypotension (132/78 → 78/40) with tachycardia (82 → 122) over 7.5 hours on POD#6 (2026-03-14)."
    chunks.append({
        "id": "vitals_trend",
        "text": vitals_text,
        "category": "vitals",
        "source": "Vitals — POD#6 trend",
        "timestamp": p["vitals"]["trend"][-1]["timestamp"],
    })

    # Clinical notes — each note as separate chunk
    for i, note in enumerate(p["clinical_notes"]):
        text = (
            f"{note['type'].upper()}: {note['title']}\n"
            f"Author: {note['author']}\n"
            f"Date: {note['timestamp']}\n\n"
            f"{note['content']}"
        )
        note_id = f"note_{i}_{note['type'].lower().replace(' ', '_')}"
        chunks.append({
            "id": note_id,
            "text": text,
            "category": "notes",
            "source": f"{note['type']} — {note['author'].split(',')[0]}",
            "timestamp": note["timestamp"],
        })

    # Imaging
    for i, img in enumerate(p["imaging"]):
        text = (
            f"IMAGING: {img['type']} — {img['study']}\n"
            f"Date: {img['timestamp']}\n"
            f"Result: {img['result']}\n"
            f"Read by: {img['read_by']}"
        )
        chunks.append({
            "id": f"imaging_{i}",
            "text": text,
            "category": "imaging",
            "source": f"{img['type']} — {img['study']}",
            "timestamp": img["timestamp"],
        })

    # Social/Family history
    sh = p["social_history"]
    chunks.append({
        "id": "social_history",
        "text": (
            f"SOCIAL HISTORY: Smoking: {sh['smoking']}. Alcohol: {sh['alcohol']}. "
            f"Occupation: {sh['occupation']}. Lives with: {sh['lives_with']}. "
            f"Advance directive: {sh['advance_directive']}."
        ),
        "category": "history",
        "source": "Social History",
        "timestamp": demo["admission_date"],
    })

    fh = p["family_history"]
    chunks.append({
        "id": "family_history",
        "text": (
            f"FAMILY HISTORY: Father — {fh['father']}. Mother — {fh['mother']}. "
            f"Siblings — {fh['siblings']}."
        ),
        "category": "history",
        "source": "Family History",
        "timestamp": demo["admission_date"],
    })

    return chunks


class PatientDataManager:
    def __init__(self):
        self.patient_data = load_patient_json()
        self.chunks = chunk_patient_data(self.patient_data)
        self.client = chromadb.Client(Settings(anonymized_telemetry=False))
        self.collection = None

    def initialize(self, embedding_fn=None, skip_chromadb: bool = False):
        """Load chunks into ChromaDB (unless skip_chromadb=True for IRIS mode)."""
        if skip_chromadb:
            print(f"[PatientData] Loaded {len(self.chunks)} chunks (IRIS mode — ChromaDB skipped)")
            return len(self.chunks)

        try:
            self.client.delete_collection("patient_data")
        except Exception:
            pass

        kwargs = {"name": "patient_data"}
        if embedding_fn:
            kwargs["embedding_function"] = embedding_fn
        self.collection = self.client.create_collection(
            **kwargs,
            metadata={"hnsw:space": "cosine"},
        )

        ids = [c["id"] for c in self.chunks]
        documents = [c["text"] for c in self.chunks]
        metadatas = [
            {"category": c["category"], "source": c["source"], "timestamp": c["timestamp"]}
            for c in self.chunks
        ]

        self.collection.add(documents=documents, ids=ids, metadatas=metadatas)
        print(f"Loaded {len(self.chunks)} chunks into ChromaDB")
        return len(self.chunks)

    def get_raw_patient_data(self) -> dict:
        return self.patient_data

    def get_all_chunks(self) -> list[dict]:
        return self.chunks
