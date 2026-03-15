"""FHIR R4 Bundle parser — converts a FHIR Bundle into the internal patient dict
format used by iris_db.load_*() and chunk_patient_data().

This allows the system to ingest standards-compliant FHIR R4 Bundles (the same
format that Epic, Cerner, and other EMRs expose) while keeping every downstream
component (IRIS tables, vector store, RAG engine, LLM calls) unchanged.
"""

from __future__ import annotations

import base64
import json
from pathlib import Path


def load_fhir_bundle(path: str | Path) -> dict:
    """Read and return a FHIR R4 Bundle JSON file."""
    with open(path) as f:
        bundle = json.load(f)
    if bundle.get("resourceType") != "Bundle":
        raise ValueError(f"Expected a FHIR Bundle, got resourceType={bundle.get('resourceType')}")
    return bundle


def _get_resources(bundle: dict, resource_type: str) -> list[dict]:
    """Extract all resources of a given type from the Bundle."""
    return [
        e["resource"]
        for e in bundle.get("entry", [])
        if e.get("resource", {}).get("resourceType") == resource_type
    ]


def _get_text(codeable_concept: dict | None, fallback: str = "") -> str:
    """Extract display text from a FHIR CodeableConcept."""
    if not codeable_concept:
        return fallback
    if codeable_concept.get("text"):
        return codeable_concept["text"]
    codings = codeable_concept.get("coding", [])
    if codings and codings[0].get("display"):
        return codings[0]["display"]
    return fallback


def _get_code(codeable_concept: dict | None) -> str:
    """Extract the code value from a FHIR CodeableConcept."""
    if not codeable_concept:
        return ""
    codings = codeable_concept.get("coding", [])
    return codings[0].get("code", "") if codings else ""


def _get_ext(resource: dict, url: str, value_key: str = "valueString") -> str | float | bool | None:
    """Get value from a FHIR extension by URL."""
    for ext in resource.get("extension", []):
        if ext.get("url") == url:
            return ext.get(value_key)
    return None


# ─── Resource Extractors ───


def extract_patient(bundle: dict) -> dict:
    """Extract Patient resource → demographics dict matching internal format."""
    patients = _get_resources(bundle, "Patient")
    if not patients:
        raise ValueError("No Patient resource found in Bundle")
    pt = patients[0]

    names = pt.get("name", [{}])
    name_obj = names[0] if names else {}
    given = " ".join(name_obj.get("given", []))
    family = name_obj.get("family", "")
    full_name = f"{given} {family}".strip()

    identifiers = pt.get("identifier", [])
    mrn = identifiers[0].get("value", "") if identifiers else ""

    birth_date = pt.get("birthDate", "")
    sex = "Male" if pt.get("gender") == "male" else "Female"

    age = _get_ext(pt, "urn:ambient-dx:age", "valueInteger")
    if age is None and birth_date:
        from datetime import date
        try:
            bd = date.fromisoformat(birth_date)
            age = (date(2026, 3, 14) - bd).days // 365
        except ValueError:
            age = 0

    return {
        "name": full_name,
        "age": age or 0,
        "sex": sex,
        "dob": birth_date,
        "mrn": mrn,
        "room": str(_get_ext(pt, "http://hl7.org/fhir/StructureDefinition/patient-room") or "").rstrip("ABCDEFGH")[:3],
        "bed": str(_get_ext(pt, "http://hl7.org/fhir/StructureDefinition/patient-room") or "")[-1:] if _get_ext(pt, "http://hl7.org/fhir/StructureDefinition/patient-room") else "",
        "admission_date": str(_get_ext(pt, "urn:ambient-dx:admission-date", "valueDate") or ""),
        "attending": str(_get_ext(pt, "urn:ambient-dx:attending") or ""),
        "code_status": str(_get_ext(pt, "urn:ambient-dx:code-status") or ""),
        "weight_kg": _get_ext(pt, "urn:ambient-dx:weight-kg", "valueDecimal") or 0,
        "height_cm": _get_ext(pt, "urn:ambient-dx:height-cm", "valueDecimal") or 0,
        "bmi": _get_ext(pt, "urn:ambient-dx:bmi", "valueDecimal") or 0,
    }


def extract_allergies(bundle: dict) -> list[dict]:
    """Extract AllergyIntolerance resources → allergy dicts matching internal format."""
    results = []
    for ai in _get_resources(bundle, "AllergyIntolerance"):
        allergen = _get_text(ai.get("code"), "Unknown")

        reactions = ai.get("reaction", [])
        reaction_text = ""
        severity = "Unknown"
        if reactions:
            manifestations = reactions[0].get("manifestation", [])
            reaction_text = manifestations[0].get("text", _get_text(manifestations[0])) if manifestations else ""
            sev_raw = reactions[0].get("severity", "")
            if ai.get("criticality") == "high":
                severity = f"Severe — Life-threatening"
            elif sev_raw == "moderate":
                severity = "Moderate"
            elif sev_raw == "severe":
                severity = "Severe — Life-threatening"
            else:
                severity = sev_raw.capitalize() if sev_raw else "Unknown"

        entry = {
            "allergen": allergen,
            "reaction": reaction_text,
            "severity": severity,
            "verified": True,
        }
        if ai.get("recordedDate"):
            entry["documented_date"] = ai["recordedDate"]
        notes = ai.get("note", [])
        if notes:
            entry["source"] = notes[0].get("text", "")
        results.append(entry)
    return results


def extract_conditions(bundle: dict) -> list[dict]:
    """Extract Condition resources → problem_list dicts matching internal format."""
    results = []
    for cond in _get_resources(bundle, "Condition"):
        problem = _get_text(cond.get("code"))
        icd10 = _get_code(cond.get("code"))

        notes = cond.get("note", [])
        status = ""
        if notes:
            status_text = notes[0].get("text", "")
            if status_text.startswith("Status: "):
                status = status_text[8:]
            else:
                status = status_text

        critical = _get_ext(cond, "urn:ambient-dx:critical-flag", "valueBoolean")

        entry = {
            "problem": problem,
            "status": status,
            "icd10": icd10,
        }
        if critical:
            entry["critical_flag"] = True
        results.append(entry)
    return results


def extract_medications(bundle: dict) -> list[dict]:
    """Extract MedicationStatement resources → medication dicts matching internal format."""
    results = []
    for ms in _get_resources(bundle, "MedicationStatement"):
        med_name = _get_text(ms.get("medicationCodeableConcept"))

        dosages = ms.get("dosage", [])
        dose_text = dosages[0].get("text", "") if dosages else ""
        route = dosages[0].get("route", {}).get("text", "") if dosages else ""

        parts = dose_text.split(" ", 1) if dose_text else ["", ""]
        if route and route in dose_text:
            dose_str = dose_text.replace(route, "").strip()
            freq_parts = dose_str.rsplit(" ", 1)
            dose = freq_parts[0] if len(freq_parts) > 1 else dose_str
            frequency = freq_parts[-1] if len(freq_parts) > 1 else ""
        else:
            dose = dose_text
            frequency = ""

        period = ms.get("effectivePeriod", {})
        start_date = period.get("start", "")

        status_raw = ms.get("status", "active")
        status = "Active" if status_raw == "active" else "Completed"
        for note in ms.get("note", []):
            txt = note.get("text", "")
            if txt.startswith("Status detail: "):
                status = txt[15:]

        reasons = ms.get("reasonCode", [])
        indication = reasons[0].get("text", "") if reasons else ""

        source = ms.get("informationSource", {})
        ordered_by = source.get("display", "") if source else ""

        notes_text = ""
        for note in ms.get("note", []):
            txt = note.get("text", "")
            if not txt.startswith("Status detail:"):
                notes_text = txt

        entry = {
            "name": med_name,
            "dose": dose,
            "route": route,
            "frequency": frequency,
            "start_date": start_date,
            "indication": indication,
            "status": status,
        }
        if ordered_by:
            entry["ordered_by"] = ordered_by
        if notes_text:
            entry["notes"] = notes_text
        if period.get("end"):
            entry["end_date"] = period["end"]
        results.append(entry)
    return results


def extract_labs(bundle: dict) -> dict:
    """Extract lab Observation resources → labs dict matching internal format.

    Returns {"timestamps": [{"label": str, "timestamp": str, "results": {lab_name: {...}}}]}
    """
    timepoints: dict[str, dict] = {}

    for obs in _get_resources(bundle, "Observation"):
        cats = obs.get("category", [])
        if not any(_get_code(c) == "laboratory" for c in cats):
            continue

        ts = obs.get("effectiveDateTime", "")
        label = str(_get_ext(obs, "urn:ambient-dx:timepoint-label") or ts)
        flag = str(_get_ext(obs, "urn:ambient-dx:flag") or "")

        lab_id = obs.get("id", "")
        lab_name = lab_id.split("-", 2)[-1] if lab_id.startswith("lab-") else _get_text(obs.get("code")).lower()

        vq = obs.get("valueQuantity", {})
        value = vq.get("value", 0)
        unit = vq.get("unit", "")

        ref_ranges = obs.get("referenceRange", [])
        ref_range = ref_ranges[0].get("text", "") if ref_ranges else ""

        if not flag:
            interps = obs.get("interpretation", [])
            if interps:
                flag = _get_text(interps[0])

        notes = obs.get("note", [])
        note_text = notes[0].get("text", "") if notes else ""

        key = f"{ts}|{label}"
        if key not in timepoints:
            timepoints[key] = {"label": label, "timestamp": ts, "results": {}}

        result = {"value": value, "unit": unit, "ref_range": ref_range, "flag": flag}
        if note_text:
            result["note"] = note_text
        timepoints[key]["results"][lab_name] = result

    sorted_tps = sorted(timepoints.values(), key=lambda x: (x["timestamp"], x["label"]))
    return {"timestamps": sorted_tps}


def extract_vitals(bundle: dict) -> dict:
    """Extract vital-signs Observation resources → vitals dict matching internal format.

    Returns {"trend": [{"timestamp": str, "label": str, "bp_systolic": int, ...}]}
    """
    vital_key_map = {
        "8480-6": "bp_systolic",
        "8462-4": "bp_diastolic",
        "8867-4": "heart_rate",
        "9279-1": "resp_rate",
        "2708-6": "spo2",
        "8310-5": "temp",
    }

    timepoints: dict[str, dict] = {}

    for obs in _get_resources(bundle, "Observation"):
        cats = obs.get("category", [])
        if not any(_get_code(c) == "vital-signs" for c in cats):
            continue

        ts = obs.get("effectiveDateTime", "")
        label = str(_get_ext(obs, "urn:ambient-dx:timepoint-label") or ts)
        loinc = _get_code(obs.get("code"))
        vital_key = vital_key_map.get(loinc)
        if not vital_key:
            continue

        vq = obs.get("valueQuantity", {})
        value = vq.get("value", 0)

        key = f"{ts}|{label}"
        if key not in timepoints:
            timepoints[key] = {
                "timestamp": ts, "label": label,
                "bp_systolic": 0, "bp_diastolic": 0,
                "heart_rate": 0, "resp_rate": 0, "spo2": 0, "temp": 0.0,
            }

        if vital_key in ("bp_systolic", "bp_diastolic", "heart_rate", "resp_rate"):
            timepoints[key][vital_key] = int(value)
        elif vital_key == "spo2":
            timepoints[key][vital_key] = int(value)
        else:
            timepoints[key][vital_key] = float(value)

    sorted_tps = sorted(timepoints.values(), key=lambda x: x["timestamp"])
    return {"trend": sorted_tps}


def extract_clinical_notes(bundle: dict) -> list[dict]:
    """Extract DocumentReference resources → clinical_notes dicts matching internal format."""
    results = []
    for doc in _get_resources(bundle, "DocumentReference"):
        note_type = str(_get_ext(doc, "urn:ambient-dx:note-type") or _get_text(doc.get("type")))
        author = doc.get("author", [{}])[0].get("display", "")
        timestamp = doc.get("date", "")
        title = doc.get("description", "")

        content_entries = doc.get("content", [])
        raw_content = ""
        if content_entries:
            attachment = content_entries[0].get("attachment", {})
            data_b64 = attachment.get("data", "")
            if data_b64:
                raw_content = base64.b64decode(data_b64).decode("utf-8")

        results.append({
            "type": note_type,
            "author": author,
            "timestamp": timestamp,
            "title": title,
            "content": raw_content,
        })
    return results


def extract_imaging(bundle: dict) -> list[dict]:
    """Extract ImagingStudy resources → imaging dicts matching internal format."""
    results = []
    for study in _get_resources(bundle, "ImagingStudy"):
        img_type = str(_get_ext(study, "urn:ambient-dx:imaging-type") or "")
        study_name = str(_get_ext(study, "urn:ambient-dx:study-name") or study.get("description", ""))
        read_by = str(_get_ext(study, "urn:ambient-dx:read-by") or "")

        notes = study.get("note", [])
        result_text = ""
        if notes:
            text = notes[0].get("text", "")
            if text.startswith("Result: "):
                result_text = text[8:]
            else:
                result_text = text

        results.append({
            "type": img_type,
            "study": study_name,
            "timestamp": study.get("started", ""),
            "result": result_text,
            "read_by": read_by,
        })
    return results


def extract_social_history(bundle: dict) -> dict:
    """Extract social history Observation → social_history dict matching internal format."""
    for obs in _get_resources(bundle, "Observation"):
        cats = obs.get("category", [])
        if any(_get_code(c) == "social-history" for c in cats):
            return {
                "smoking": str(_get_ext(obs, "urn:ambient-dx:smoking") or ""),
                "alcohol": str(_get_ext(obs, "urn:ambient-dx:alcohol") or ""),
                "occupation": str(_get_ext(obs, "urn:ambient-dx:occupation") or ""),
                "lives_with": str(_get_ext(obs, "urn:ambient-dx:lives-with") or ""),
                "advance_directive": str(_get_ext(obs, "urn:ambient-dx:advance-directive") or ""),
            }
    return {"smoking": "", "alcohol": "", "occupation": "", "lives_with": "", "advance_directive": ""}


def extract_family_history(bundle: dict) -> dict:
    """Extract FamilyMemberHistory → family_history dict matching internal format."""
    for fmh in _get_resources(bundle, "FamilyMemberHistory"):
        return {
            "father": str(_get_ext(fmh, "urn:ambient-dx:father") or ""),
            "mother": str(_get_ext(fmh, "urn:ambient-dx:mother") or ""),
            "siblings": str(_get_ext(fmh, "urn:ambient-dx:siblings") or ""),
        }
    return {"father": "", "mother": "", "siblings": ""}


# ─── Main Conversion ───


def to_patient_dict(bundle: dict) -> dict:
    """Convert a FHIR R4 Bundle into the internal patient dict format.

    The output matches the shape of patient_robert_chen.json["patient"],
    so chunk_patient_data() and all iris_db.load_*() functions work unchanged.
    """
    return {
        "demographics": extract_patient(bundle),
        "allergies": extract_allergies(bundle),
        "problem_list": extract_conditions(bundle),
        "current_medications": extract_medications(bundle),
        "labs": extract_labs(bundle),
        "vitals": extract_vitals(bundle),
        "clinical_notes": extract_clinical_notes(bundle),
        "imaging": extract_imaging(bundle),
        "social_history": extract_social_history(bundle),
        "family_history": extract_family_history(bundle),
    }
