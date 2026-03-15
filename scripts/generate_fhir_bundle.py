#!/usr/bin/env python3
"""Generate a FHIR R4 Bundle from the custom patient JSON.

Reads backend/data/patient_robert_chen.json and writes
backend/data/patient_robert_chen_fhir.json as a standards-compliant
FHIR R4 Bundle with proper resource types, coding systems, and references.
"""

import json
import base64
from pathlib import Path

SRC = Path(__file__).resolve().parent.parent / "backend" / "data" / "patient_robert_chen.json"
DST = SRC.parent / "patient_robert_chen_fhir.json"

PATIENT_ID = "P001"
ENCOUNTER_ID = "enc-tka-2026"

LOINC = "http://loinc.org"
ICD10 = "http://hl7.org/fhir/sid/icd-10-cm"
RXNORM = "http://www.nlm.nih.gov/research/umls/rxnorm"
SNOMED = "http://snomed.info/sct"
ALLERGY_CLINICAL = "http://terminology.hl7.org/CodeSystem/allergyintolerance-clinical"
ALLERGY_CATEGORY = "http://hl7.org/fhir/allergy-intolerance-category"
CONDITION_CLINICAL = "http://terminology.hl7.org/CodeSystem/condition-clinical"
MED_STATUS = "http://hl7.org/fhir/CodeSystem/medication-statement-status"
OBS_CATEGORY = "http://terminology.hl7.org/CodeSystem/observation-category"
DOC_TYPE = "http://loinc.org"

LAB_LOINC = {
    "hemoglobin":  ("718-7",   "Hemoglobin [Mass/volume] in Blood"),
    "hematocrit":  ("4544-3",  "Hematocrit [Volume Fraction] of Blood"),
    "platelets":   ("777-3",   "Platelets [#/volume] in Blood"),
    "wbc":         ("6690-2",  "Leukocytes [#/volume] in Blood"),
    "bun":         ("3094-0",  "Urea nitrogen [Mass/volume] in Serum or Plasma"),
    "creatinine":  ("2160-0",  "Creatinine [Mass/volume] in Serum or Plasma"),
    "sodium":      ("2951-2",  "Sodium [Moles/volume] in Serum or Plasma"),
    "potassium":   ("2823-3",  "Potassium [Moles/volume] in Serum or Plasma"),
    "glucose":     ("2345-7",  "Glucose [Mass/volume] in Serum or Plasma"),
    "inr":         ("6301-6",  "INR in Platelet poor plasma by Coagulation assay"),
    "pt":          ("5902-2",  "Prothrombin time (PT)"),
    "aptt":        ("3173-2",  "aPTT in Blood by Coagulation assay"),
    "lactate":     ("2524-7",  "Lactate [Moles/volume] in Serum or Plasma"),
    "d_dimer":     ("48065-7", "Fibrin D-dimer FEU [Mass/volume] in Platelet poor plasma"),
    "fibrinogen":  ("3255-7",  "Fibrinogen [Mass/volume] in Platelet poor plasma"),
    "troponin":    ("6598-7",  "Troponin T cardiac [Mass/volume] in Serum or Plasma"),
    "pro_bnp":     ("33762-6", "NT-proBNP [Mass/volume] in Serum or Plasma"),
}

VITAL_LOINC = {
    "bp_systolic":  ("8480-6", "Systolic blood pressure"),
    "bp_diastolic": ("8462-4", "Diastolic blood pressure"),
    "heart_rate":   ("8867-4", "Heart rate"),
    "resp_rate":    ("9279-1", "Respiratory rate"),
    "spo2":         ("2708-6", "Oxygen saturation in Arterial blood by Pulse oximetry"),
    "temp":         ("8310-5", "Body temperature"),
}

VITAL_UNITS = {
    "bp_systolic": ("mmHg", "mm[Hg]"),
    "bp_diastolic": ("mmHg", "mm[Hg]"),
    "heart_rate": ("/min", "/min"),
    "resp_rate": ("/min", "/min"),
    "spo2": ("%", "%"),
    "temp": ("Cel", "Cel"),
}

MED_RXNORM = {
    "Heparin": ("5224", "Heparin"),
    "Metformin": ("6809", "Metformin"),
    "Lisinopril": ("29046", "Lisinopril"),
    "Atorvastatin": ("83367", "Atorvastatin"),
    "Tamsulosin": ("77492", "Tamsulosin"),
    "Morphine PCA": ("7052", "Morphine"),
    "Ondansetron": ("26225", "Ondansetron"),
    "Pantoprazole": ("40790", "Pantoprazole"),
    "Cefazolin": ("2180", "Cefazolin"),
}

ALLERGEN_CODES = {
    "Penicillin": (RXNORM, "7980", "Penicillin"),
    "Sulfa Drugs": (RXNORM, "10831", "Sulfonamide"),
    "Contrast Dye (IV)": (SNOMED, "39290007", "Iodinated contrast media"),
    "Heparin": (RXNORM, "5224", "Heparin"),
}


def ref(resource_type, rid):
    return {"reference": f"{resource_type}/{rid}"}


def coding(system, code, display, text=None):
    result = {"coding": [{"system": system, "code": code, "display": display}]}
    if text:
        result["text"] = text
    return result


def entry(resource):
    return {"fullUrl": f"urn:uuid:{resource['resourceType']}/{resource['id']}", "resource": resource}


def make_patient(demo):
    parts = demo["name"].split()
    return {
        "resourceType": "Patient",
        "id": PATIENT_ID,
        "identifier": [{"system": "urn:oid:hospital-mrn", "value": demo["mrn"]}],
        "name": [{"use": "official", "family": parts[-1], "given": parts[:-1]}],
        "gender": "male" if demo["sex"] == "Male" else "female",
        "birthDate": demo["dob"],
        "extension": [
            {"url": "http://hl7.org/fhir/StructureDefinition/patient-room", "valueString": f"{demo['room']}{demo['bed']}"},
            {"url": "urn:ambient-dx:admission-date", "valueDate": demo["admission_date"]},
            {"url": "urn:ambient-dx:attending", "valueString": demo["attending"]},
            {"url": "urn:ambient-dx:code-status", "valueString": demo["code_status"]},
            {"url": "urn:ambient-dx:weight-kg", "valueDecimal": demo["weight_kg"]},
            {"url": "urn:ambient-dx:height-cm", "valueDecimal": demo["height_cm"]},
            {"url": "urn:ambient-dx:bmi", "valueDecimal": demo["bmi"]},
        ],
    }


def make_encounter(demo):
    return {
        "resourceType": "Encounter",
        "id": ENCOUNTER_ID,
        "status": "in-progress",
        "class": {"system": "http://terminology.hl7.org/CodeSystem/v3-ActCode", "code": "IMP", "display": "inpatient encounter"},
        "subject": ref("Patient", PATIENT_ID),
        "period": {"start": f"{demo['admission_date']}T00:00:00"},
        "location": [{"location": {"display": f"Room {demo['room']}{demo['bed']}"}}],
        "participant": [{"individual": {"display": demo["attending"]}}],
    }


def make_allergy(i, a):
    severity_map = {"Moderate": "moderate", "Severe": "severe"}
    sev_raw = a["severity"].split("\u00e2\u20ac\u201d")[0].split(" —")[0].split(" –")[0].strip()
    sev = severity_map.get(sev_raw, "moderate")
    criticality = "high" if "Life-threatening" in a["severity"] or "Severe" in a["severity"] else "low"

    allergen_key = a["allergen"]
    code_sys, code_val, code_disp = ALLERGEN_CODES.get(allergen_key, (SNOMED, "unknown", allergen_key))

    res = {
        "resourceType": "AllergyIntolerance",
        "id": f"allergy-{i}",
        "clinicalStatus": coding(ALLERGY_CLINICAL, "active", "Active"),
        "verificationStatus": coding("http://terminology.hl7.org/CodeSystem/allergyintolerance-verification", "confirmed", "Confirmed"),
        "type": "allergy",
        "criticality": criticality,
        "code": coding(code_sys, code_val, code_disp, text=allergen_key),
        "patient": ref("Patient", PATIENT_ID),
        "recordedDate": a.get("documented_date", ""),
        "reaction": [{
            "manifestation": [{"text": a["reaction"]}],
            "severity": sev,
        }],
    }
    if a.get("source"):
        res["note"] = [{"text": a["source"]}]
    return res


def make_condition(i, prob):
    clinical = "active"
    if "Resolved" in prob["status"]:
        clinical = "resolved"
    elif "Historical" in prob["status"]:
        clinical = "inactive"

    res = {
        "resourceType": "Condition",
        "id": f"condition-{i}",
        "clinicalStatus": coding(CONDITION_CLINICAL, clinical, clinical.capitalize()),
        "code": coding(ICD10, prob.get("icd10", ""), prob["problem"]),
        "subject": ref("Patient", PATIENT_ID),
        "encounter": ref("Encounter", ENCOUNTER_ID),
        "note": [{"text": f"Status: {prob['status']}"}],
    }
    if prob.get("critical_flag"):
        res["severity"] = coding(SNOMED, "24484000", "Severe")
        res["extension"] = [{"url": "urn:ambient-dx:critical-flag", "valueBoolean": True}]
    return res


def make_medication(i, med):
    status = "active" if "Active" in med["status"] else "completed"
    med_name = med["name"]
    rxn_code, rxn_display = MED_RXNORM.get(med_name, ("unknown", med_name))

    res = {
        "resourceType": "MedicationStatement",
        "id": f"med-{i}",
        "status": status,
        "medicationCodeableConcept": coding(RXNORM, rxn_code, rxn_display, text=med_name),
        "subject": ref("Patient", PATIENT_ID),
        "effectivePeriod": {"start": med["start_date"]},
        "dosage": [{
            "text": f"{med['dose']} {med['route']} {med['frequency']}",
            "route": {"text": med["route"]},
        }],
        "reasonCode": [{"text": med["indication"]}],
        "note": [],
    }
    if med.get("end_date"):
        res["effectivePeriod"]["end"] = med["end_date"]
    if med.get("ordered_by"):
        res["informationSource"] = {"display": med["ordered_by"]}
    if med.get("notes"):
        res["note"].append({"text": med["notes"]})
    status_note = med["status"]
    if status_note != "Active" and status_note != "Completed":
        res["note"].append({"text": f"Status detail: {status_note}"})
    if not res["note"]:
        del res["note"]
    return res


def flag_to_interpretation(flag):
    flag_lower = flag.lower()
    if "critical" in flag_lower and "high" in flag_lower:
        return ("HH", "Critical high")
    if "critical" in flag_lower and "low" in flag_lower:
        return ("LL", "Critical low")
    if "critical" in flag_lower:
        return ("AA", "Critical abnormal")
    if "high" in flag_lower:
        return ("H", "High")
    if "low" in flag_lower:
        return ("L", "Low")
    if "borderline" in flag_lower:
        return ("H", "High")
    if "normal" in flag_lower:
        return ("N", "Normal")
    return ("N", "Normal")


def make_lab_observation(tp_idx, tp_label, timestamp, lab_name, val_obj):
    loinc_code, loinc_display = LAB_LOINC.get(lab_name, ("unknown", lab_name))
    interp_code, interp_display = flag_to_interpretation(val_obj["flag"])

    obs = {
        "resourceType": "Observation",
        "id": f"lab-{tp_idx}-{lab_name}",
        "status": "final",
        "category": [coding(OBS_CATEGORY, "laboratory", "Laboratory")],
        "code": coding(LOINC, loinc_code, loinc_display),
        "subject": ref("Patient", PATIENT_ID),
        "encounter": ref("Encounter", ENCOUNTER_ID),
        "effectiveDateTime": timestamp,
        "valueQuantity": {
            "value": val_obj["value"],
            "unit": val_obj["unit"],
        },
        "interpretation": [coding("http://terminology.hl7.org/CodeSystem/v3-ObservationInterpretation", interp_code, interp_display)],
        "referenceRange": [{"text": val_obj["ref_range"]}],
        "extension": [
            {"url": "urn:ambient-dx:timepoint-label", "valueString": tp_label},
            {"url": "urn:ambient-dx:flag", "valueString": val_obj["flag"]},
        ],
    }
    if val_obj.get("note"):
        obs["note"] = [{"text": val_obj["note"]}]
    return obs


def make_vital_observation(v_idx, vital_key, value, timestamp, label):
    loinc_code, loinc_display = VITAL_LOINC[vital_key]
    unit_display, unit_code = VITAL_UNITS[vital_key]

    return {
        "resourceType": "Observation",
        "id": f"vital-{v_idx}-{vital_key}",
        "status": "final",
        "category": [coding(OBS_CATEGORY, "vital-signs", "Vital Signs")],
        "code": coding(LOINC, loinc_code, loinc_display),
        "subject": ref("Patient", PATIENT_ID),
        "encounter": ref("Encounter", ENCOUNTER_ID),
        "effectiveDateTime": timestamp,
        "valueQuantity": {
            "value": value,
            "unit": unit_display,
            "system": "http://unitsofmeasure.org",
            "code": unit_code,
        },
        "extension": [{"url": "urn:ambient-dx:timepoint-label", "valueString": label}],
    }


def make_document_reference(i, note):
    content_b64 = base64.b64encode(note["content"].encode("utf-8")).decode("ascii")

    note_type = note["type"].lower().replace(" ", "-")
    loinc_map = {
        "surgical-note": ("11504-8", "Surgical operation note"),
        "progress-note": ("11506-3", "Progress note"),
        "nursing-note": ("34746-8", "Nurse Note"),
        "discharge-summary": ("18842-5", "Discharge summary"),
    }
    type_code, type_display = loinc_map.get(note_type, ("47039-3", "Hospital Admission note"))

    return {
        "resourceType": "DocumentReference",
        "id": f"doc-{i}",
        "status": "current",
        "type": coding(LOINC, type_code, type_display),
        "subject": ref("Patient", PATIENT_ID),
        "date": note["timestamp"],
        "author": [{"display": note["author"]}],
        "description": note["title"],
        "content": [{
            "attachment": {
                "contentType": "text/plain",
                "data": content_b64,
            }
        }],
        "extension": [{"url": "urn:ambient-dx:note-type", "valueString": note["type"]}],
    }


def make_imaging_study(i, img):
    modality_map = {
        "X-ray": ("DX", "Digital Radiography"),
        "Chest X-ray": ("DX", "Digital Radiography"),
        "Ultrasound": ("US", "Ultrasound"),
    }
    mod_code, mod_display = modality_map.get(img["type"], ("OT", "Other"))

    return {
        "resourceType": "ImagingStudy",
        "id": f"imaging-{i}",
        "status": "available",
        "subject": ref("Patient", PATIENT_ID),
        "started": img["timestamp"],
        "modality": [{"system": "http://dicom.nema.org/resources/ontology/DCM", "code": mod_code, "display": mod_display}],
        "description": f"{img['type']} — {img['study']}",
        "note": [{"text": f"Result: {img['result']}"}],
        "extension": [
            {"url": "urn:ambient-dx:study-name", "valueString": img["study"]},
            {"url": "urn:ambient-dx:read-by", "valueString": img["read_by"]},
            {"url": "urn:ambient-dx:imaging-type", "valueString": img["type"]},
        ],
    }


def make_family_history(fh):
    return {
        "resourceType": "FamilyMemberHistory",
        "id": "family-history-1",
        "status": "completed",
        "patient": ref("Patient", PATIENT_ID),
        "relationship": coding("http://terminology.hl7.org/CodeSystem/v3-RoleCode", "FAMMEMB", "family member"),
        "extension": [
            {"url": "urn:ambient-dx:father", "valueString": fh["father"]},
            {"url": "urn:ambient-dx:mother", "valueString": fh["mother"]},
            {"url": "urn:ambient-dx:siblings", "valueString": fh["siblings"]},
        ],
    }


def make_social_history_observation(sh):
    return {
        "resourceType": "Observation",
        "id": "social-history",
        "status": "final",
        "category": [coding(OBS_CATEGORY, "social-history", "Social History")],
        "code": coding(LOINC, "29762-2", "Social history Narrative"),
        "subject": ref("Patient", PATIENT_ID),
        "valueString": (
            f"Smoking: {sh['smoking']}. "
            f"Alcohol: {sh['alcohol']}. "
            f"Occupation: {sh['occupation']}. "
            f"Lives with: {sh['lives_with']}. "
            f"Advance directive: {sh['advance_directive']}."
        ),
        "extension": [
            {"url": "urn:ambient-dx:smoking", "valueString": sh["smoking"]},
            {"url": "urn:ambient-dx:alcohol", "valueString": sh["alcohol"]},
            {"url": "urn:ambient-dx:occupation", "valueString": sh["occupation"]},
            {"url": "urn:ambient-dx:lives-with", "valueString": sh["lives_with"]},
            {"url": "urn:ambient-dx:advance-directive", "valueString": sh["advance_directive"]},
        ],
    }


def main():
    with open(SRC) as f:
        data = json.load(f)
    p = data["patient"]

    entries = []

    # Patient
    entries.append(entry(make_patient(p["demographics"])))
    entries.append(entry(make_encounter(p["demographics"])))

    # Allergies
    for i, a in enumerate(p["allergies"]):
        entries.append(entry(make_allergy(i, a)))

    # Conditions
    for i, prob in enumerate(p["problem_list"]):
        entries.append(entry(make_condition(i, prob)))

    # Medications
    for i, med in enumerate(p["current_medications"]):
        entries.append(entry(make_medication(i, med)))

    # Lab observations
    for tp_idx, tp in enumerate(p["labs"]["timestamps"]):
        for lab_name, val_obj in tp["results"].items():
            entries.append(entry(make_lab_observation(tp_idx, tp["label"], tp["timestamp"], lab_name, val_obj)))

    # Vital sign observations
    for v_idx, v in enumerate(p["vitals"]["trend"]):
        for vital_key in ("bp_systolic", "bp_diastolic", "heart_rate", "resp_rate", "spo2", "temp"):
            entries.append(entry(make_vital_observation(v_idx, vital_key, v[vital_key], v["timestamp"], v["label"])))

    # Clinical notes as DocumentReference
    for i, note in enumerate(p["clinical_notes"]):
        entries.append(entry(make_document_reference(i, note)))

    # Imaging studies
    for i, img in enumerate(p["imaging"]):
        entries.append(entry(make_imaging_study(i, img)))

    # Family history
    entries.append(entry(make_family_history(p["family_history"])))

    # Social history as Observation
    entries.append(entry(make_social_history_observation(p["social_history"])))

    bundle = {
        "resourceType": "Bundle",
        "id": "patient-robert-chen-bundle",
        "type": "collection",
        "timestamp": "2026-03-14T13:30:00Z",
        "total": len(entries),
        "entry": entries,
    }

    with open(DST, "w") as f:
        json.dump(bundle, f, indent=2, ensure_ascii=False)

    resource_types = {}
    for e in entries:
        rt = e["resource"]["resourceType"]
        resource_types[rt] = resource_types.get(rt, 0) + 1

    print(f"Generated FHIR R4 Bundle: {DST}")
    print(f"Total entries: {len(entries)}")
    for rt, count in sorted(resource_types.items()):
        print(f"  {rt}: {count}")


if __name__ == "__main__":
    main()
