"""Pre-cached LLM responses for demo reliability when APIs are slow."""

CACHED_RESPONSES = {
    1: {
        "intents": {
            "has_clinical_intent": True,
            "intents": [
                {
                    "type": "diagnostic_query",
                    "summary": "Acute hypotension in post-operative patient on heparin drip",
                    "diagnostic_question": "What is causing acute hemodynamic instability (BP 78/40, HR 122) in a POD#6 TKA patient on heparin?",
                    "data_needed": [
                        {"category": "vitals", "specifics": "Recent vital sign trends"},
                        {"category": "labs", "specifics": "CBC, BMP, coags, lactate"},
                        {"category": "medications", "specifics": "Current medications especially anticoagulation"},
                        {"category": "notes", "specifics": "Recent nursing and progress notes"},
                    ],
                    "differentials_mentioned": ["hemorrhage", "sepsis", "PE", "cardiac"],
                    "urgency": "critical",
                    "clinical_context": "Rapid response called for acute decompensation in post-surgical patient. Fluid-unresponsive hypotension suggests serious etiology.",
                }
            ],
            "action_items": [
                {"action": "Fluid resuscitation", "priority": "stat", "status": "ordered"},
                {"action": "STAT labs including type and screen", "priority": "stat", "status": "discussed"},
            ],
        },
        "diagnostic": {
            "patient_summary": {
                "one_liner": "67M POD#6 R TKA presenting with acute hypotension (78/40) and tachycardia (122) on heparin drip, unresponsive to fluid resuscitation",
                "active_situation": "Rapid response called for hemodynamic instability. Progressive deterioration over 7.5 hours with accelerating decline in last 90 minutes.",
            },
            "critical_alerts": [
                {
                    "severity": "critical",
                    "finding": "Acute hemodynamic instability unresponsive to fluids",
                    "evidence": "BP 132/78 at 06:00 → 78/40 at 13:30, HR 82 → 122. 1L NS bolus without improvement.",
                    "source": "Vitals — POD#6 trend; Nursing Note — RN Torres 13:30",
                    "action_required": "Emergent evaluation for cause of shock. Consider vasopressors if ongoing hypotension.",
                }
            ],
            "differential_diagnoses": [
                {
                    "diagnosis": "Hemorrhagic Shock (GI Bleed vs Surgical Site)",
                    "likelihood": "high",
                    "evidence_for": [
                        {"finding": "Hemoglobin drop from 13.2 to 8.2 g/dL over 6 days, with 1.9 g/dL drop in last 24h", "source": "Lab Trend — Hemoglobin", "strength": "strong"},
                        {"finding": "Dark stool noted by nursing", "source": "Nursing Note — RN Torres 10:30", "strength": "moderate"},
                        {"finding": "BUN elevated to 34 from baseline 18 (upper GI bleed pattern)", "source": "Labs — POD#6", "strength": "moderate"},
                        {"finding": "Patient on heparin anticoagulation increasing bleed risk", "source": "Medication List — Heparin", "strength": "moderate"},
                    ],
                    "evidence_against": [
                        {"finding": "On pantoprazole for stress ulcer prophylaxis", "source": "Medication List — Pantoprazole", "strength": "weak"},
                    ],
                    "data_gaps": ["Stool guaiac not performed", "No CT abdomen/pelvis", "Type and screen pending"],
                    "recommended_workup": ["STAT stool guaiac", "Type and crossmatch 2 units pRBC", "Consider CT angiography if stabilized", "Surgical site exam for hematoma"],
                },
                {
                    "diagnosis": "Pulmonary Embolism",
                    "likelihood": "moderate",
                    "evidence_for": [
                        {"finding": "POD#6 from major orthopedic surgery (high VTE risk)", "source": "Surgical Note — Dr. Mitchell", "strength": "strong"},
                        {"finding": "Tachycardia HR 122, hypoxia SpO2 92%", "source": "Vitals — POD#6 trend", "strength": "moderate"},
                        {"finding": "D-dimer markedly elevated at 4.2", "source": "Labs — POD#6", "strength": "moderate"},
                        {"finding": "Family history: brother with DVT at age 60", "source": "Family History", "strength": "weak"},
                    ],
                    "evidence_against": [
                        {"finding": "Patient on therapeutic heparin (aPTT 72 on POD#5)", "source": "Labs — POD#5", "strength": "moderate"},
                        {"finding": "Pre-op venous duplex negative", "source": "Ultrasound — Bilateral LE Venous Duplex", "strength": "weak"},
                    ],
                    "data_gaps": ["CT pulmonary angiography not performed", "No repeat lower extremity duplex", "No echocardiogram"],
                    "recommended_workup": ["CTPA when hemodynamically stable", "Bedside echocardiogram", "Repeat bilateral LE duplex"],
                },
                {
                    "diagnosis": "Sepsis",
                    "likelihood": "low",
                    "evidence_for": [
                        {"finding": "Temperature trending up to 38.0°C", "source": "Vitals — POD#6 trend", "strength": "weak"},
                        {"finding": "WBC elevated to 12.1", "source": "Labs — POD#6", "strength": "weak"},
                        {"finding": "Lactate elevated to 2.8", "source": "Labs — POD#6", "strength": "moderate"},
                    ],
                    "evidence_against": [
                        {"finding": "Surgical site clean per nursing assessment", "source": "Nursing Note — RN Torres 06:30", "strength": "moderate"},
                        {"finding": "Completed prophylactic antibiotics without issue", "source": "Medication List — Cefazolin", "strength": "weak"},
                    ],
                    "data_gaps": ["Blood cultures not sent", "Urinalysis not done", "Procalcitonin not ordered"],
                    "recommended_workup": ["Blood cultures x2", "Urinalysis", "Chest X-ray"],
                },
            ],
            "clinical_scores": [],
            "suggested_actions": [
                {"action": "STAT Type and Crossmatch, transfuse 2u pRBC", "priority": "immediate", "rationale": "Hgb 8.2 with active hemodynamic instability"},
                {"action": "Stool guaiac", "priority": "immediate", "rationale": "Dark stool + Hgb drop + elevated BUN suggests upper GI bleed"},
                {"action": "Consider GI consult", "priority": "urgent", "rationale": "Possible GI hemorrhage source"},
                {"action": "Recheck coagulation studies", "priority": "urgent", "rationale": "On heparin with supratherapeutic aPTT (98 sec)"},
            ],
        },
        "safety": {"safety_alerts": [], "no_alerts": True},
    },
    2: {
        "intents": {
            "has_clinical_intent": True,
            "intents": [
                {
                    "type": "diagnostic_query",
                    "summary": "Evaluation for GI bleed as cause of hemoglobin drop and hypotension",
                    "diagnostic_question": "Is this patient having an acute upper GI bleed causing hemorrhagic shock?",
                    "data_needed": [
                        {"category": "labs", "specifics": "Hemoglobin trend, BUN, BUN/Cr ratio"},
                        {"category": "medications", "specifics": "Anticoagulation, GI prophylaxis"},
                        {"category": "notes", "specifics": "Stool description, GI symptoms"},
                        {"category": "vitals", "specifics": "Hemodynamic trends"},
                    ],
                    "differentials_mentioned": ["GI bleed", "upper GI hemorrhage"],
                    "urgency": "critical",
                    "clinical_context": "Hemoglobin dropped 3.2 g/dL in 24 hours with dark stool and rising BUN — classic upper GI bleed pattern.",
                }
            ],
            "action_items": [
                {"action": "Stool guaiac test", "priority": "stat", "status": "discussed"},
                {"action": "GI consult for possible EGD", "priority": "urgent", "status": "discussed"},
            ],
        },
        "diagnostic": {
            "patient_summary": {
                "one_liner": "67M POD#6 R TKA with acute hemorrhagic shock — evaluating for upper GI bleed",
                "active_situation": "Progressive anemia (Hgb 11.4→8.2 in 48h) with dark stool, elevated BUN (34), on heparin anticoagulation. Classic upper GI bleed presentation.",
            },
            "critical_alerts": [
                {
                    "severity": "critical",
                    "finding": "Rapid hemoglobin decline suggesting active hemorrhage",
                    "evidence": "Hgb 11.4 (POD#3) → 10.1 (POD#5) → 8.2 (POD#6). Accelerating: 1.9 g/dL drop in 24h vs 1.3 over prior 48h.",
                    "source": "Lab Trend — Hemoglobin",
                    "action_required": "Transfuse pRBC. Type and crossmatch. Consider reversing anticoagulation.",
                },
                {
                    "severity": "warning",
                    "finding": "Supratherapeutic anticoagulation with aPTT 98 sec",
                    "evidence": "aPTT 98 sec (target 60-80) despite no dose change. May indicate consumptive coagulopathy or DIC.",
                    "source": "Labs — POD#6",
                    "action_required": "Hold heparin drip. Recheck aPTT, fibrinogen, D-dimer.",
                },
            ],
            "differential_diagnoses": [
                {
                    "diagnosis": "Upper GI Hemorrhage",
                    "likelihood": "high",
                    "evidence_for": [
                        {"finding": "Hemoglobin drop 1.9 g/dL in 24 hours (10.1→8.2)", "source": "Lab Trend — Hemoglobin", "strength": "strong"},
                        {"finding": "Dark stool — new finding noted by nursing", "source": "Nursing Note — RN Torres 10:30", "strength": "strong"},
                        {"finding": "BUN/Creatinine ratio 26:1 (BUN 34, Cr 1.3) — elevated, suggestive of upper GI source", "source": "Labs — POD#6", "strength": "moderate"},
                        {"finding": "On heparin anticoagulation — increased bleeding risk", "source": "Medication List — Heparin", "strength": "moderate"},
                        {"finding": "Stress of major surgery — risk factor for stress ulcers", "source": "Surgical Note — Dr. Mitchell", "strength": "moderate"},
                    ],
                    "evidence_against": [
                        {"finding": "On pantoprazole 40mg IV daily for stress ulcer prophylaxis", "source": "Medication List — Pantoprazole", "strength": "weak"},
                        {"finding": "No prior history of GI bleeding or peptic ulcer disease", "source": "Problem List", "strength": "weak"},
                    ],
                    "data_gaps": ["Stool guaiac not performed", "No EGD", "No CT angiography"],
                    "recommended_workup": ["STAT stool guaiac", "GI consult for emergent EGD", "CT angiography abdomen if EGD delayed"],
                },
                {
                    "diagnosis": "Pulmonary Embolism",
                    "likelihood": "moderate",
                    "evidence_for": [
                        {"finding": "POD#6 from major orthopedic surgery — very high VTE risk", "source": "Surgical Note — Dr. Mitchell", "strength": "strong"},
                        {"finding": "Tachycardia (122) and hypoxia (SpO2 92%)", "source": "Vitals — POD#6 trend", "strength": "moderate"},
                        {"finding": "D-dimer 4.2 (markedly elevated)", "source": "Labs — POD#6", "strength": "moderate"},
                    ],
                    "evidence_against": [
                        {"finding": "GI bleed better explains hemoglobin drop", "source": "Lab Trend — Hemoglobin", "strength": "moderate"},
                        {"finding": "On therapeutic heparin", "source": "Medication List — Heparin", "strength": "moderate"},
                    ],
                    "data_gaps": ["CTPA not done", "Echo not done"],
                    "recommended_workup": ["CTPA", "Bedside echocardiogram", "Troponin trend"],
                },
            ],
            "clinical_scores": [
                {
                    "score_name": "Glasgow-Blatchford Bleeding Score",
                    "calculated_value": "12 (High risk)",
                    "interpretation": "High risk for needing intervention. Score ≥6 warrants urgent endoscopy.",
                    "components": [
                        {"criterion": "BUN ≥6.5 and <8.0 mmol/L (BUN 34 mg/dL = 12.1 mmol/L)", "value": "≥8.0", "points": "6", "source": "Labs — POD#6"},
                        {"criterion": "Hemoglobin (male) 10-12", "value": "8.2 — <10", "points": "6", "source": "Labs — POD#6"},
                        {"criterion": "Systolic BP <90", "value": "78", "points": "3", "source": "Vitals — POD#6 13:30"},
                        {"criterion": "Heart rate ≥100", "value": "122", "points": "1", "source": "Vitals — POD#6 13:30"},
                    ],
                }
            ],
            "suggested_actions": [
                {"action": "STAT stool guaiac", "priority": "immediate", "rationale": "Confirm GI source of bleeding"},
                {"action": "Hold heparin drip — aPTT supratherapeutic at 98", "priority": "immediate", "rationale": "Active bleeding with supratherapeutic anticoagulation"},
                {"action": "Transfuse 2 units pRBC", "priority": "immediate", "rationale": "Hgb 8.2 with active hemorrhage and hemodynamic instability"},
                {"action": "GI consult for emergent EGD", "priority": "urgent", "rationale": "High Glasgow-Blatchford score, likely upper GI source"},
            ],
        },
        "safety": {"safety_alerts": [], "no_alerts": True},
    },
    3: {
        "intents": {
            "has_clinical_intent": True,
            "intents": [
                {
                    "type": "differential_diagnosis",
                    "summary": "Evaluating PE as cause of hemodynamic instability in post-TKA patient",
                    "diagnostic_question": "Could this patient have a pulmonary embolism despite being on heparin? What is the Wells score? What are the platelets doing?",
                    "data_needed": [
                        {"category": "vitals", "specifics": "Heart rate, SpO2, BP trends"},
                        {"category": "labs", "specifics": "D-dimer, platelets trend, coagulation studies"},
                        {"category": "medications", "specifics": "Heparin dosing and aPTT monitoring"},
                        {"category": "history", "specifics": "VTE history, surgical history"},
                        {"category": "scores", "specifics": "Wells PE criteria, 4Ts HIT score"},
                    ],
                    "differentials_mentioned": ["pulmonary embolism", "HIT", "heparin-induced thrombocytopenia"],
                    "urgency": "critical",
                    "clinical_context": "Team questioning PE on heparin — implicit question about heparin efficacy and platelet trend raises HIT concern. Recent orthopedic surgery is major VTE risk factor.",
                }
            ],
            "action_items": [
                {"action": "Calculate Wells PE score", "priority": "stat", "status": "discussed"},
                {"action": "Check platelet trend", "priority": "stat", "status": "discussed"},
                {"action": "CT pulmonary angiography", "priority": "urgent", "status": "discussed"},
            ],
        },
        "diagnostic": {
            "patient_summary": {
                "one_liner": "67M POD#6 R TKA in hemorrhagic shock with concurrent >50% platelet decline on heparin — CRITICAL: prior documented HIT (2023)",
                "active_situation": "CRITICAL SAFETY FINDING: Patient has DOCUMENTED Heparin-Induced Thrombocytopenia from 2023 (confirmed PF4 antibody + serotonin release assay) and is currently receiving heparin with platelets dropping >63% from baseline. This is a life-threatening medication error.",
            },
            "critical_alerts": [
                {
                    "severity": "critical",
                    "finding": "HEPARIN CONTRAINDICATED — Active HIT recurrence. Patient has documented HIT history (2023) with confirmed PF4 antibody and SRA. Currently on heparin drip with platelets dropping 63.7% (245→89). STOP HEPARIN IMMEDIATELY.",
                    "evidence": "2023 Discharge Summary documents HIT with PF4 antibody OD 2.4 and positive SRA. Allergy list documents 'Heparin — HIT, Severe — Life-threatening.' Current platelet trend: 245→220→178→132→89 (63.7% decline over 6 days of heparin exposure). 4Ts score: 7/8 (High probability).",
                    "source": "Discharge Summary — Dr. James Park, Hematology, 2023-11-20; Allergy List; Lab Trend — Platelets; Medication List — Heparin",
                    "action_required": "1) STOP heparin drip IMMEDIATELY. 2) Start argatroban 2 mcg/kg/min (per 2023 successful treatment). 3) STAT PF4/heparin antibody. 4) Hematology consult STAT. 5) Avoid ALL heparin products including flushes.",
                },
                {
                    "severity": "critical",
                    "finding": "Active hemorrhage with hemoglobin decline",
                    "evidence": "Hgb 13.2→8.2 over 6 days with 1.9 g/dL drop in last 24h. Dark stool. BUN 34 (up from 18).",
                    "source": "Lab Trend — Hemoglobin; Nursing Note — RN Torres 10:30; Labs — POD#6",
                    "action_required": "Transfuse pRBC. Investigate source (GI vs DIC from HIT).",
                },
            ],
            "differential_diagnoses": [
                {
                    "diagnosis": "Heparin-Induced Thrombocytopenia (HIT) — Recurrence",
                    "likelihood": "high",
                    "evidence_for": [
                        {"finding": "DOCUMENTED prior HIT in 2023 with positive PF4 antibody (OD 2.4) and positive serotonin release assay", "source": "Discharge Summary — Dr. James Park, Hematology, 2023-11-20", "strength": "strong"},
                        {"finding": "Heparin allergy documented as 'Severe — Life-threatening'", "source": "Allergy List", "strength": "strong"},
                        {"finding": "Platelet decline >50% from baseline: 245→89 K/uL (63.7% decline)", "source": "Lab Trend — Platelets", "strength": "strong"},
                        {"finding": "Timing: platelet decline beginning ~day 5 of heparin re-exposure (earlier onset expected with re-exposure within 100 days)", "source": "Lab Trend — Platelets; Medication List — Heparin", "strength": "strong"},
                        {"finding": "Supratherapeutic aPTT (98) without dose change — may indicate consumptive coagulopathy", "source": "Labs — POD#6", "strength": "moderate"},
                        {"finding": "D-dimer markedly elevated at 4.2, fibrinogen low at 180 — thrombotic microangiopathy", "source": "Labs — POD#6", "strength": "moderate"},
                    ],
                    "evidence_against": [
                        {"finding": "Other causes of thrombocytopenia possible (hemodilution, sepsis) — but magnitude and pattern most consistent with HIT", "source": "Clinical reasoning", "strength": "weak"},
                    ],
                    "data_gaps": ["PF4/heparin antibody not yet sent", "SRA not yet sent", "No imaging for new thrombosis"],
                    "recommended_workup": ["STAT PF4/heparin ELISA", "Serotonin release assay", "Bilateral LE duplex ultrasound", "CT chest/abdomen/pelvis with contrast for thrombosis survey"],
                },
                {
                    "diagnosis": "Pulmonary Embolism (possibly HIT-related thrombosis)",
                    "likelihood": "high",
                    "evidence_for": [
                        {"finding": "POD#6 from major orthopedic surgery", "source": "Surgical Note — Dr. Mitchell", "strength": "strong"},
                        {"finding": "Wells score: 7 points (High probability)", "source": "Calculated below", "strength": "strong"},
                        {"finding": "Tachycardia (122), hypoxia (SpO2 92%), hypotension", "source": "Vitals — POD#6 trend", "strength": "strong"},
                        {"finding": "D-dimer 4.2 (markedly elevated)", "source": "Labs — POD#6", "strength": "moderate"},
                        {"finding": "If HIT is active, heparin would be INEFFECTIVE and PROTHROMBOTIC — increasing PE risk", "source": "Clinical reasoning + HIT history", "strength": "strong"},
                        {"finding": "Family history: brother with DVT at age 60", "source": "Family History", "strength": "weak"},
                    ],
                    "evidence_against": [
                        {"finding": "Pre-op duplex was negative", "source": "Ultrasound — Bilateral LE Venous Duplex", "strength": "weak"},
                    ],
                    "data_gaps": ["CTPA not performed", "Echocardiogram not done", "Troponin trending"],
                    "recommended_workup": ["STAT CTPA", "Bedside echocardiogram for RV strain", "Troponin trend", "Consider catheter-directed therapy if massive PE confirmed"],
                },
                {
                    "diagnosis": "Upper GI Hemorrhage",
                    "likelihood": "moderate",
                    "evidence_for": [
                        {"finding": "Hemoglobin drop 10.1→8.2 in 24h", "source": "Lab Trend — Hemoglobin", "strength": "strong"},
                        {"finding": "Dark stool", "source": "Nursing Note — RN Torres 10:30", "strength": "moderate"},
                        {"finding": "BUN/Cr ratio 26:1 (elevated)", "source": "Labs — POD#6", "strength": "moderate"},
                    ],
                    "evidence_against": [
                        {"finding": "On pantoprazole prophylaxis", "source": "Medication List — Pantoprazole", "strength": "weak"},
                        {"finding": "Bleeding could be from DIC/consumption in HIT", "source": "Clinical reasoning", "strength": "moderate"},
                    ],
                    "data_gaps": ["Stool guaiac", "EGD"],
                    "recommended_workup": ["Stool guaiac", "GI consult", "Consider EGD after stabilization"],
                },
            ],
            "clinical_scores": [
                {
                    "score_name": "Wells Score for PE",
                    "calculated_value": "7.0 points — High probability (>6 points)",
                    "interpretation": "High pre-test probability for PE. CTPA indicated regardless of D-dimer. In context of possible HIT, PE may be HIT-related arterial/venous thrombosis.",
                    "components": [
                        {"criterion": "Clinical signs/symptoms of DVT", "value": "Not assessed currently", "points": "0", "source": "No LE exam documented today"},
                        {"criterion": "PE is #1 diagnosis or equally likely", "value": "Yes — major differential", "points": "3", "source": "Clinical assessment"},
                        {"criterion": "Heart rate > 100", "value": "HR 122", "points": "1.5", "source": "Vitals — POD#6 13:30"},
                        {"criterion": "Immobilization/surgery in previous 4 weeks", "value": "R TKA 6 days ago", "points": "1.5", "source": "Surgical Note — Dr. Mitchell"},
                        {"criterion": "Previous DVT/PE", "value": "DVT 2023", "points": "1.5", "source": "Problem List — DVT left LE 2023"},
                        {"criterion": "Hemoptysis", "value": "No", "points": "0", "source": "No hemoptysis reported"},
                        {"criterion": "Malignancy", "value": "No", "points": "0", "source": "Problem List — no malignancy"}
                    ],
                },
                {
                    "score_name": "4Ts Score for HIT (Current Episode)",
                    "calculated_value": "7/8 — High probability (≥6 points)",
                    "interpretation": "HIGH probability of HIT. Pre-test probability >60%. MUST discontinue heparin immediately and start alternative anticoagulation. Do not wait for confirmatory testing.",
                    "components": [
                        {"criterion": "Thrombocytopenia: >50% fall AND nadir ≥20", "value": "63.7% fall (245→89), nadir 89", "points": "2", "source": "Lab Trend — Platelets"},
                        {"criterion": "Timing of platelet fall: days 5-10 of exposure OR ≤1 day if prior exposure within 30 days", "value": "Day 6 of heparin exposure. Also prior HIT in 2023.", "points": "2", "source": "Medication List — Heparin (start 2026-02-24); Discharge Summary 2023"},
                        {"criterion": "Thrombosis or other sequelae", "value": "Suspected PE (tachycardia, hypoxia, elevated D-dimer). Prior HIT associated with DVT.", "points": "2", "source": "Vitals; Labs — POD#6; Discharge Summary 2023"},
                        {"criterion": "Other causes of thrombocytopenia", "value": "Possible (hemodilution, sepsis) but less likely given magnitude and pattern", "points": "1", "source": "Clinical assessment"}
                    ],
                },
            ],
            "suggested_actions": [
                {"action": "STOP HEPARIN DRIP IMMEDIATELY", "priority": "immediate", "rationale": "Documented HIT history with active platelet decline >50%. Continued heparin is life-threatening."},
                {"action": "Start argatroban 2 mcg/kg/min IV", "priority": "immediate", "rationale": "Alternative anticoagulant. Successfully used in 2023 HIT episode per discharge summary."},
                {"action": "STAT PF4/heparin antibody ELISA", "priority": "immediate", "rationale": "Confirm HIT recurrence. Do NOT wait for results to stop heparin."},
                {"action": "Hematology consult STAT", "priority": "immediate", "rationale": "HIT management, anticoagulation transition, thrombosis workup"},
                {"action": "STAT CTPA", "priority": "immediate", "rationale": "High Wells score (7), possible HIT-related PE"},
                {"action": "Transfuse pRBC — avoid heparin-coated lines", "priority": "immediate", "rationale": "Hgb 8.2 with active hemodynamic instability. Ensure all equipment is heparin-free."},
                {"action": "Remove all heparin-containing flushes and lines", "priority": "immediate", "rationale": "Patient must have zero heparin exposure per HIT protocol"},
            ],
        },
        "safety": {
            "safety_alerts": [
                {
                    "severity": "critical",
                    "type": "contraindication",
                    "medication": "Heparin (unfractionated) — 18 units/kg/hr IV continuous",
                    "historical_event": "Heparin-Induced Thrombocytopenia (HIT) confirmed November 2023 with positive PF4/heparin antibody (OD 2.4) and positive serotonin release assay. 4Ts score 7/8. Platelets dropped from 198 to 68 (66% decline). Required argatroban bridge to warfarin.",
                    "historical_source": "Discharge Summary — Dr. James Park, Hematology, 2023-11-20",
                    "current_source": "Medication List — Heparin (Active, started 2026-02-24); Lab Trend — Platelets (245→89, 63.7% decline)",
                    "risk": "LIFE-THREATENING: HIT recurrence with >50% platelet decline. HIT causes paradoxical prothrombotic state — risk of PE, stroke, limb ischemia, death. Heparin allergy alert was OVERRIDDEN in the system per surgical note.",
                    "recommended_action": "1) STOP heparin immediately. 2) Start argatroban. 3) STAT PF4 antibody. 4) Hematology consult. 5) Avoid ALL heparin products. 6) Flag allergy override for safety review.",
                }
            ],
            "no_alerts": False,
        },
    },
}
