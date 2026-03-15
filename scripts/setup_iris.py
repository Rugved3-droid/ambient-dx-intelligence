#!/usr/bin/env python3
"""One-time IRIS setup: create tables, load synthetic patient data, build embeddings.

Usage:
    python scripts/setup_iris.py          # load from custom JSON (default)
    python scripts/setup_iris.py --fhir   # load from FHIR R4 Bundle
"""

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))

from app.storage.iris_db import (
    test_connection,
    create_tables,
    load_medications,
    load_allergies,
    load_problems,
    load_labs,
    load_vitals,
)
from app.storage.iris_vector_store import create_vector_table, upsert_chunks
from app.data.patient_manager import load_patient_json, chunk_patient_data

PATIENT_ID = "P001"
USE_FHIR = "--fhir" in sys.argv

FHIR_BUNDLE_PATH = Path(__file__).resolve().parent.parent / "backend" / "data" / "patient_robert_chen_fhir.json"


def wait_for_iris(max_retries: int = 15, delay: float = 3.0):
    """Wait for IRIS container to be ready, with retries."""
    print("[Setup] Waiting for IRIS to be ready...")
    for attempt in range(1, max_retries + 1):
        if test_connection():
            print(f"[Setup] IRIS connected (attempt {attempt})")
            return True
        print(f"  Attempt {attempt}/{max_retries} — retrying in {delay}s...")
        time.sleep(delay)
    print("[Setup] ERROR: Could not connect to IRIS. Is Docker running?")
    print("  Start it with: docker compose up -d")
    sys.exit(1)


def main():
    print("=" * 50)
    print("  Ambient Dx — IRIS Setup")
    print("=" * 50)

    wait_for_iris()

    # Load patient data (FHIR Bundle or custom JSON)
    print("\n[1/4] Loading patient data...")
    if USE_FHIR and FHIR_BUNDLE_PATH.exists():
        from app.data.fhir_parser import load_fhir_bundle, to_patient_dict
        print("  Source: FHIR R4 Bundle")
        bundle = load_fhir_bundle(FHIR_BUNDLE_PATH)
        patient = to_patient_dict(bundle)
        patient_data = {"patient": patient}
    else:
        if USE_FHIR:
            print(f"  WARNING: --fhir requested but {FHIR_BUNDLE_PATH} not found, falling back to custom JSON")
        print("  Source: Custom JSON")
        patient_data = load_patient_json()
        patient = patient_data["patient"]
    print(f"  Patient: {patient['demographics']['name']}")

    # Create structured tables
    print("\n[2/4] Creating IRIS tables...")
    create_tables()
    create_vector_table()

    # Load structured data
    print("\n[3/4] Loading structured data into IRIS...")
    n_meds = load_medications(patient, PATIENT_ID)
    n_allergies = load_allergies(patient, PATIENT_ID)
    n_problems = load_problems(patient, PATIENT_ID)
    n_labs = load_labs(patient, PATIENT_ID)
    n_vitals = load_vitals(patient, PATIENT_ID)
    print(f"  Loaded: {n_meds} medications, {n_allergies} allergies, "
          f"{n_problems} problems, {n_labs} lab results, {n_vitals} vital signs")

    # Chunk and embed for vector search
    print("\n[4/4] Building embeddings and loading into IRIS vector store...")
    chunks = chunk_patient_data(patient_data)
    print(f"  Created {len(chunks)} chunks from patient data")

    t0 = time.time()
    n_vectors = upsert_chunks(chunks, PATIENT_ID)
    elapsed = time.time() - t0
    print(f"  Embedded and stored {n_vectors} vectors in {elapsed:.1f}s")

    print("\n" + "=" * 50)
    print("  IRIS setup complete!")
    print(f"  Management Portal: http://localhost:52773/csp/sys/UtilHome.csp")
    print(f"  Login: demo / demo")
    print("=" * 50)


if __name__ == "__main__":
    main()
