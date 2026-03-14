#!/usr/bin/env python3
"""Smoke test: verify IRIS integration is working end-to-end.

Usage:
    python scripts/smoke_test.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))

passed = 0
failed = 0


def check(name: str, condition: bool, detail: str = ""):
    global passed, failed
    if condition:
        passed += 1
        print(f"  PASS  {name}")
    else:
        failed += 1
        print(f"  FAIL  {name}{f' — {detail}' if detail else ''}")


def main():
    print("=" * 50)
    print("  Ambient Dx — IRIS Smoke Test")
    print("=" * 50)

    # 1. Connection
    print("\n[1] IRIS Connection")
    from iris_db import test_connection
    check("IRIS reachable", test_connection())

    # 2. Structured queries
    print("\n[2] Structured Retrieval")
    from iris_db import (
        get_medications, get_allergies, get_problems,
        get_critical_problems, get_lab_trend, get_vitals_trend,
        get_heparin_status, PATIENT_ID,
    )

    meds = get_medications(PATIENT_ID)
    check("Medications loaded", len(meds) > 0, f"got {len(meds)}")
    check("Heparin in meds", any("heparin" in m["text"].lower() for m in meds))

    allergies = get_allergies(PATIENT_ID)
    check("Allergies loaded", len(allergies) > 0, f"got {len(allergies)}")
    check("HIT allergy present", any("heparin" in a["text"].lower() for a in allergies))

    problems = get_problems(PATIENT_ID)
    check("Problems loaded", len(problems) > 0)

    critical = get_critical_problems(PATIENT_ID)
    check("Critical problem (HIT) flagged", len(critical) > 0)
    if critical:
        check("Critical problem mentions HIT", "hit" in critical[0]["text"].lower())

    plt_trend = get_lab_trend(PATIENT_ID, "platelets")
    check("Platelet trend available", len(plt_trend) > 0)

    vitals = get_vitals_trend(PATIENT_ID)
    check("Vitals trend available", len(vitals) > 0)

    hep_status = get_heparin_status(PATIENT_ID)
    check("Heparin active status detected", len(hep_status) > 0)

    # 3. Vector search
    print("\n[3] Vector Search")
    from iris_vector_store import similarity_search, get_chunk_count

    count = get_chunk_count(PATIENT_ID)
    check(f"Vector chunks in IRIS", count > 0, f"got {count}")

    hit_results = similarity_search("heparin induced thrombocytopenia", patient_id=PATIENT_ID, top_k=5)
    check("HIT vector search returns results", len(hit_results) > 0, f"got {len(hit_results)}")
    if hit_results:
        top_text = hit_results[0]["text"].lower()
        check("Top result relevant to HIT/heparin",
              "heparin" in top_text or "hit" in top_text or "thrombocytopenia" in top_text)

    hypo_results = similarity_search("acute hypotension post-operative", patient_id=PATIENT_ID, top_k=5)
    check("Hypotension vector search returns results", len(hypo_results) > 0)

    # 4. Hybrid retrieval via RAGEngine
    print("\n[4] Hybrid Retrieval (RAGEngine)")
    from patient_data import PatientDataManager
    from rag_engine import RAGEngine

    pm = PatientDataManager()
    pm.initialize(skip_chromadb=True)
    rag = RAGEngine(pm, use_iris=True)

    results = rag.retrieve("What are the patient's platelets doing?", n_results=10)
    check("Hybrid retrieval returns results", len(results) > 0, f"got {len(results)}")
    cats = {r["category"] for r in results}
    check("Hybrid retrieval includes structured data", "labs" in cats or "medications" in cats)
    check("Hybrid retrieval includes notes", "notes" in cats)

    safety = rag.retrieve_for_safety()
    check("Safety retrieval returns results", len(safety) > 0, f"got {len(safety)}")
    check("Safety includes allergies", any(r["category"] == "allergies" for r in safety))
    check("Safety includes medications", any(r["category"] == "medications" for r in safety))

    # Summary
    print("\n" + "=" * 50)
    total = passed + failed
    print(f"  Results: {passed}/{total} passed, {failed} failed")
    if failed == 0:
        print("  All checks passed!")
    print("=" * 50)
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
