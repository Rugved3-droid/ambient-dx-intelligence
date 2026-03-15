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
    from app.storage.iris_db import test_connection
    check("IRIS reachable", test_connection())

    # 2. Structured queries
    print("\n[2] Structured Retrieval")
    from app.storage.iris_db import (
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
    from app.storage.iris_vector_store import similarity_search, get_chunk_count

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
    from app.data.patient_manager import PatientDataManager
    from app.retrieval.engine import RAGEngine

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

    # 5. FHIR R4 Bundle parsing
    print("\n[5] FHIR R4 Bundle Parsing")
    from pathlib import Path as P
    fhir_path = P(__file__).resolve().parent.parent / "backend" / "data" / "patient_robert_chen_fhir.json"
    check("FHIR Bundle file exists", fhir_path.exists())

    if fhir_path.exists():
        from app.data.fhir_parser import load_fhir_bundle, to_patient_dict
        from app.data.patient_manager import load_patient_json

        bundle = load_fhir_bundle(fhir_path)
        check("FHIR Bundle is valid", bundle.get("resourceType") == "Bundle")
        check("FHIR Bundle has entries", len(bundle.get("entry", [])) > 100)

        fhir_patient = to_patient_dict(bundle)
        orig_patient = load_patient_json()["patient"]

        check("FHIR demographics name matches",
              fhir_patient["demographics"]["name"] == orig_patient["demographics"]["name"])
        check("FHIR allergy count matches",
              len(fhir_patient["allergies"]) == len(orig_patient["allergies"]))
        check("FHIR medication count matches",
              len(fhir_patient["current_medications"]) == len(orig_patient["current_medications"]))
        check("FHIR lab timepoint count matches",
              len(fhir_patient["labs"]["timestamps"]) == len(orig_patient["labs"]["timestamps"]))
        check("FHIR vitals count matches",
              len(fhir_patient["vitals"]["trend"]) == len(orig_patient["vitals"]["trend"]))
        check("FHIR note count matches",
              len(fhir_patient["clinical_notes"]) == len(orig_patient["clinical_notes"]))
        check("FHIR imaging count matches",
              len(fhir_patient["imaging"]) == len(orig_patient["imaging"]))

        fhir_lab_names = set()
        for tp in fhir_patient["labs"]["timestamps"]:
            fhir_lab_names.update(tp["results"].keys())
        orig_lab_names = set()
        for tp in orig_patient["labs"]["timestamps"]:
            orig_lab_names.update(tp["results"].keys())
        check("FHIR lab names match", fhir_lab_names == orig_lab_names,
              f"fhir={sorted(fhir_lab_names)}, orig={sorted(orig_lab_names)}")

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
