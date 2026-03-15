"""Golden test dataset for Ragas evaluation.

Each entry contains a clinical question, the ground-truth answer derived from
cached_responses.py and patient_robert_chen.json, and the chunk sources that a
correct retrieval *must* include.
"""

GOLDEN_DATASET: list[dict] = [
    # ── Wells score (from CACHED_QUERY_RESPONSES) ──────────────────────
    {
        "question": "What's the Wells score for PE on this patient?",
        "ground_truth": (
            "Wells Score for PE: 4.5 points (Moderate Risk). "
            "Components: Heart rate >100 (+1.5 pts, HR 122 bpm) [Vitals — POD#6 13:30]; "
            "Surgery within 4 weeks (+1.5 pts, R TKA 2026-03-09) [Op Note — Dr. Park]; "
            "Previous DVT/PE (+1.5 pts, L LE DVT 2023-07-10) [Discharge Summary — Dr. Thompson]; "
            "Clinical signs of DVT (0 pts, not documented); "
            "PE most likely diagnosis (0 pts, GI bleed also likely); "
            "Hemoptysis (0 pts, none reported); "
            "Malignancy (0 pts, no active malignancy). "
            "D-dimer is markedly elevated at 4.2 µg/mL. CTPA is indicated."
        ),
        "expected_sources": [
            "Vitals — POD#6 trend",
            "Lab Trend — Platelets",
            "Problem List",
        ],
    },
    # ── Platelet trend (from CACHED_QUERY_RESPONSES) ───────────────────
    {
        "question": "Show me the platelet trend",
        "ground_truth": (
            "Platelet Trend (POD#1 through POD#6): "
            "Pre-op 245, POD#1 220, POD#3 198, POD#5 156, POD#6 89 K/µL. "
            "Total decline: 59.5% from admission baseline (220→89). "
            "Heparin started POD#1 (2026-03-10). Current day of heparin exposure: Day 4. "
            "CRITICAL: Patient has DOCUMENTED prior HIT (2023) — PF4 antibody OD 2.4, "
            "positive SRA. Heparin is listed as a severe/life-threatening allergy. "
            "This platelet decline pattern is consistent with HIT recurrence "
            "(onset day 4-5 of re-exposure)."
        ),
        "expected_sources": [
            "Lab Trend — Platelets",
            "Allergy List",
            "Medication List — Heparin",
        ],
    },
    # ── Hemoglobin trend ───────────────────────────────────────────────
    {
        "question": "What is the patient's hemoglobin trend?",
        "ground_truth": (
            "Hemoglobin trend: Pre-op 13.2, POD#1 12.1, POD#3 11.4, "
            "POD#5 10.1, POD#6 8.2 g/dL. Rate of decline: 12.1 → 8.2 g/dL "
            "over 4 days (3.9 g/dL drop), accelerating with a 1.9 g/dL drop "
            "in the last 24 hours. This rapid decline suggests active hemorrhage."
        ),
        "expected_sources": [
            "Lab Trend — Hemoglobin",
        ],
    },
    # ── Heparin safety ─────────────────────────────────────────────────
    {
        "question": "Is heparin safe for this patient?",
        "ground_truth": (
            "NO — Heparin is CONTRAINDICATED. The patient has documented "
            "Heparin-Induced Thrombocytopenia (HIT) from 2023, confirmed with "
            "positive PF4 antibody (OD 2.4) and positive serotonin release assay. "
            "Heparin is listed as a severe/life-threatening allergy. The patient "
            "is currently receiving heparin 18 units/kg/hr IV with platelets "
            "declining 59.5% (220→89 K/µL). Heparin must be stopped immediately "
            "and replaced with argatroban."
        ),
        "expected_sources": [
            "Allergy List",
            "Medication List — Heparin",
            "Problem List",
            "Lab Trend — Platelets",
        ],
    },
    # ── Current medications ────────────────────────────────────────────
    {
        "question": "What medications is the patient currently on?",
        "ground_truth": (
            "Current medications: Heparin 18 units/kg/hr IV continuous (VTE prophylaxis, "
            "started 2026-03-10); Metformin 1000 mg PO BID (T2DM, held POD#0-2); "
            "Lisinopril 20 mg PO daily (hypertension); Atorvastatin 40 mg PO daily "
            "at bedtime (hyperlipidemia); Tamsulosin 0.4 mg PO daily (BPH); "
            "Morphine PCA 1 mg demand IV PRN (post-op pain); Ondansetron 4 mg IV "
            "Q6H PRN (nausea); Pantoprazole 40 mg IV daily (stress ulcer prophylaxis); "
            "Cefazolin 2 g IV Q8H (surgical prophylaxis, completed)."
        ),
        "expected_sources": [
            "Medication List — Summary",
        ],
    },
    # ── Allergies ──────────────────────────────────────────────────────
    {
        "question": "Does the patient have any allergies?",
        "ground_truth": (
            "Yes. Documented allergies: (1) Penicillin — rash, moderate severity; "
            "(2) Sulfa Drugs — urticarial rash, moderate severity; "
            "(3) Contrast Dye (IV) — anaphylaxis, severe/life-threatening; "
            "(4) Heparin — Heparin-Induced Thrombocytopenia (HIT) confirmed with "
            "positive PF4 antibody and serotonin release assay (2023), "
            "severe/life-threatening."
        ),
        "expected_sources": [
            "Allergy List",
        ],
    },
    # ── Hypotension differential ───────────────────────────────────────
    {
        "question": "What could be causing the patient's hypotension?",
        "ground_truth": (
            "Differential for acute hypotension (BP 78/40, HR 122): "
            "(1) Hemorrhagic shock / GI bleed — HIGH likelihood: Hgb drop "
            "13.2→8.2, dark stool, elevated BUN 34, on heparin. "
            "(2) Pulmonary embolism — MODERATE: POD#6 from TKA, tachycardia, "
            "SpO2 92%, D-dimer 4.2, prior DVT history. "
            "(3) Sepsis — LOW: temp 38.0, WBC 12.1, lactate 2.8, but surgical "
            "site clean. "
            "Progressive deterioration from BP 132/78 to 78/40 over 7.5 hours."
        ),
        "expected_sources": [
            "Vitals — POD#6 trend",
            "Lab Trend — Hemoglobin",
        ],
    },
    # ── Latest labs ────────────────────────────────────────────────────
    {
        "question": "What were the latest lab results?",
        "ground_truth": (
            "Latest labs (POD#6, 2026-03-14 06:00): Hemoglobin 8.2 g/dL (Low), "
            "Hematocrit 24.6% (Low), Platelets 89 K/uL (Low), WBC 12.1 K/uL (High), "
            "BUN 34 mg/dL (High), Creatinine 1.3 mg/dL (Normal), Sodium 138 mEq/L, "
            "Potassium 4.8 mEq/L, Glucose 142 mg/dL (High), Lactate 2.8 mmol/L (High), "
            "aPTT 98 sec (High — supratherapeutic, target 60-80), INR 1.4, "
            "D-dimer 4.2 µg/mL (High), Fibrinogen 180 mg/dL (Low-normal)."
        ),
        "expected_sources": [
            "Labs — POD#6",
        ],
    },
    # ── HIT history ────────────────────────────────────────────────────
    {
        "question": "Does this patient have a history of HIT?",
        "ground_truth": (
            "Yes. The patient has a DOCUMENTED history of Heparin-Induced "
            "Thrombocytopenia (HIT) from November 2023. Confirmed with PF4 "
            "antibody (OD 2.4) and positive serotonin release assay. "
            "Platelets dropped from 198 to 68 (66% decline) during that episode. "
            "Treated with argatroban bridge to warfarin. Heparin is listed as a "
            "severe/life-threatening allergy. HIT is flagged as CRITICAL in the "
            "problem list with the note 'AVOID ALL HEPARIN PRODUCTS'."
        ),
        "expected_sources": [
            "Allergy List",
            "Problem List",
        ],
    },
    # ── Surgical history ───────────────────────────────────────────────
    {
        "question": "What is the patient's surgical history?",
        "ground_truth": (
            "The patient underwent a right total knee arthroplasty (TKA) on "
            "2026-03-09 by Dr. Sarah Mitchell. Currently POD#6. The surgery "
            "was performed for right knee osteoarthritis. The patient's prior "
            "surgical/medical history also includes a left lower extremity DVT "
            "in 2023 and hospitalization for HIT in November 2023."
        ),
        "expected_sources": [
            "Problem List",
        ],
    },
    # ── 4Ts score ──────────────────────────────────────────────────────
    {
        "question": "Calculate the 4Ts score for HIT",
        "ground_truth": (
            "4Ts Score for HIT: 6-7/8 — High probability (>=6 points). "
            "Components: Thrombocytopenia — >50% fall (59.5%, 220→89), nadir 89 "
            "(2 points) [Lab Trend — Platelets]; "
            "Timing — Day 4-5 of heparin exposure + prior HIT 2023 "
            "(2 points) [Medication List + Discharge Summary]; "
            "Thrombosis — Suspected PE (tachycardia, hypoxia, elevated D-dimer) "
            "(1-2 points) [Vitals + Labs]; "
            "Other causes — Possible but less likely given magnitude/pattern "
            "(1 point) [Clinical assessment]. "
            "Must discontinue heparin immediately. Do not wait for confirmatory testing."
        ),
        "expected_sources": [
            "Lab Trend — Platelets",
            "Medication List — Heparin",
            "Allergy List",
        ],
    },
    # ── BUN/Creatinine ratio ───────────────────────────────────────────
    {
        "question": "What is the patient's BUN/creatinine ratio?",
        "ground_truth": (
            "BUN 34 mg/dL, Creatinine 1.3 mg/dL. BUN/Creatinine ratio = 26:1 "
            "(elevated; normal <20:1). An elevated BUN/Cr ratio (>20:1) in the "
            "setting of hemoglobin decline and dark stool is suggestive of an "
            "upper GI bleed source. BUN was previously 18 mg/dL on admission."
        ),
        "expected_sources": [
            "Labs — POD#6",
        ],
    },
    # ── Imaging ────────────────────────────────────────────────────────
    {
        "question": "What imaging has been done on this patient?",
        "ground_truth": (
            "Imaging studies performed: (1) Pre-op chest X-ray (2026-03-08) — "
            "mild cardiomegaly, no acute process, read by Dr. Williams. "
            "(2) Right knee X-ray post-op (2026-03-09) — prosthesis in good "
            "alignment, read by Dr. Williams. "
            "(3) Bilateral lower extremity venous duplex ultrasound (2026-03-08) — "
            "negative for DVT, read by Dr. Adams."
        ),
        "expected_sources": [],
    },
    # ── PE risk ────────────────────────────────────────────────────────
    {
        "question": "Is the patient at risk for PE?",
        "ground_truth": (
            "Yes, the patient is at HIGH risk for PE. Risk factors: (1) POD#6 "
            "from major orthopedic surgery (TKA) — very high VTE risk. "
            "(2) Prior DVT: left LE DVT in 2023. (3) Family history: brother "
            "with DVT at age 60. (4) Current signs: tachycardia HR 122, "
            "hypoxia SpO2 92%, hypotension BP 78/40, D-dimer 4.2. "
            "Wells score calculates to 4.5 points (moderate pre-test probability). "
            "If HIT is active, heparin would be ineffective and prothrombotic, "
            "further increasing PE risk. CTPA is indicated."
        ),
        "expected_sources": [
            "Vitals — POD#6 trend",
            "Problem List",
        ],
    },
    # ── Current vital signs ────────────────────────────────────────────
    {
        "question": "What are the patient's current vital signs?",
        "ground_truth": (
            "Latest vital signs (POD#6 13:30, 2026-03-14): BP 78/40 mmHg, "
            "HR 122 bpm, RR 24, SpO2 92%, Temp 38.0°C. "
            "Trend over POD#6: BP 132/78 (06:00) → 118/72 (10:00) → "
            "95/58 (13:00) → 78/40 (13:30). HR 82 → 88 → 108 → 122. "
            "Progressive hypotension with tachycardia over 7.5 hours, "
            "with accelerating decline in the last 90 minutes. "
            "1L NS bolus given without improvement."
        ),
        "expected_sources": [
            "Vitals — POD#6 trend",
        ],
    },
]
