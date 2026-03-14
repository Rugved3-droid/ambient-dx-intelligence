import React, { useState, useMemo } from 'react'

/* ════════════════════════════════════════════════════════════════════
   NOISE DATA — Additional data for EMR realism and clutter
   ════════════════════════════════════════════════════════════════════ */

const HISTORICAL_VITALS = [
  { date: '02/23', time: '06:00', bp: '138/82', hr: 78, rr: 16, spo2: 98, temp: 36.8, pain: 2, label: 'Pre-op' },
  { date: '02/23', time: '10:00', bp: '136/80', hr: 76, rr: 16, spo2: 97, temp: 36.9, pain: 5, label: 'Pre-op' },
  { date: '02/23', time: '14:30', bp: '142/88', hr: 92, rr: 18, spo2: 96, temp: 37.0, pain: 7, label: 'Post-op' },
  { date: '02/23', time: '18:00', bp: '134/82', hr: 88, rr: 18, spo2: 96, temp: 37.1, pain: 7, label: 'Post-op' },
  { date: '02/23', time: '22:00', bp: '130/78', hr: 84, rr: 16, spo2: 97, temp: 37.1, pain: 6, label: 'Post-op' },
  { date: '02/24', time: '02:00', bp: '126/74', hr: 80, rr: 14, spo2: 97, temp: 37.0, pain: 5, label: 'POD#1' },
  { date: '02/24', time: '06:00', bp: '128/76', hr: 80, rr: 16, spo2: 97, temp: 37.0, pain: 5, label: 'POD#1' },
  { date: '02/24', time: '10:00', bp: '132/80', hr: 78, rr: 16, spo2: 97, temp: 36.9, pain: 4, label: 'POD#1' },
  { date: '02/24', time: '14:00', bp: '126/74', hr: 82, rr: 16, spo2: 96, temp: 37.1, pain: 6, label: 'POD#1' },
  { date: '02/24', time: '22:00', bp: '130/76', hr: 76, rr: 14, spo2: 97, temp: 37.0, pain: 4, label: 'POD#1' },
  { date: '02/25', time: '06:00', bp: '134/80', hr: 74, rr: 16, spo2: 97, temp: 36.8, pain: 3, label: 'POD#2' },
  { date: '02/25', time: '12:00', bp: '128/78', hr: 78, rr: 16, spo2: 97, temp: 37.0, pain: 4, label: 'POD#2' },
  { date: '02/25', time: '18:00', bp: '130/76', hr: 76, rr: 14, spo2: 97, temp: 36.9, pain: 3, label: 'POD#2' },
  { date: '02/25', time: '22:00', bp: '126/74', hr: 72, rr: 14, spo2: 98, temp: 36.8, pain: 2, label: 'POD#2' },
  { date: '02/26', time: '06:00', bp: '132/78', hr: 76, rr: 16, spo2: 97, temp: 37.0, pain: 3, label: 'POD#3' },
  { date: '02/26', time: '12:00', bp: '128/76', hr: 74, rr: 16, spo2: 98, temp: 36.9, pain: 2, label: 'POD#3' },
  { date: '02/26', time: '18:00', bp: '130/78', hr: 78, rr: 14, spo2: 97, temp: 37.1, pain: 3, label: 'POD#3' },
  { date: '02/26', time: '22:00', bp: '126/74', hr: 72, rr: 14, spo2: 97, temp: 36.8, pain: 2, label: 'POD#3' },
  { date: '02/27', time: '06:00', bp: '134/80', hr: 74, rr: 16, spo2: 98, temp: 36.9, pain: 2, label: 'POD#4' },
  { date: '02/27', time: '12:00', bp: '130/78', hr: 76, rr: 16, spo2: 97, temp: 37.0, pain: 2, label: 'POD#4' },
  { date: '02/27', time: '18:00', bp: '128/76', hr: 78, rr: 16, spo2: 97, temp: 37.1, pain: 2, label: 'POD#4' },
  { date: '02/27', time: '22:00', bp: '126/74', hr: 74, rr: 14, spo2: 97, temp: 36.8, pain: 1, label: 'POD#4' },
  { date: '02/28', time: '06:00', bp: '130/78', hr: 78, rr: 16, spo2: 97, temp: 37.0, pain: 2, label: 'POD#5' },
  { date: '02/28', time: '12:00', bp: '128/76', hr: 80, rr: 16, spo2: 96, temp: 37.2, pain: 2, label: 'POD#5' },
  { date: '02/28', time: '18:00', bp: '126/74', hr: 82, rr: 18, spo2: 96, temp: 37.3, pain: 2, label: 'POD#5' },
  { date: '02/28', time: '22:00', bp: '124/72', hr: 84, rr: 16, spo2: 96, temp: 37.1, pain: 2, label: 'POD#5' },
]

const TODAY_VITALS = [
  { date: '03/01', time: '06:00', bp: '132/78', hr: 82, rr: 16, spo2: 97, temp: 37.1, pain: 2, label: 'POD#6' },
  { date: '03/01', time: '08:00', bp: '128/76', hr: 85, rr: 16, spo2: 96, temp: 37.2, pain: 3, label: 'POD#6' },
  { date: '03/01', time: '10:00', bp: '118/72', hr: 92, rr: 18, spo2: 95, temp: 37.4, pain: 3, label: 'POD#6' },
  { date: '03/01', time: '12:00', bp: '105/65', hr: 102, rr: 20, spo2: 94, temp: 37.6, pain: 4, label: 'POD#6' },
  { date: '03/01', time: '13:00', bp: '88/52', hr: 115, rr: 22, spo2: 93, temp: 37.8, pain: 5, label: 'POD#6' },
  { date: '03/01', time: '13:30', bp: '78/40', hr: 122, rr: 24, spo2: 92, temp: 38.0, pain: 6, label: 'POD#6' },
]

const EXTRA_MEDICATIONS = [
  { name: 'Aspirin', dose: '81 mg', route: 'PO', frequency: 'Daily', start_date: '2022-01-15', indication: 'Cardiovascular prophylaxis', status: 'Home Med — held peri-op', ordered_by: 'PCP' },
  { name: 'Vitamin D3', dose: '2000 IU', route: 'PO', frequency: 'Daily', start_date: '2023-06-01', indication: 'Supplement', status: 'Home Med — Active', ordered_by: 'PCP' },
  { name: 'Omega-3 Fish Oil', dose: '1000 mg', route: 'PO', frequency: 'Daily', start_date: '2023-06-01', indication: 'Cardiovascular', status: 'Home Med — Active', ordered_by: 'PCP' },
  { name: 'Calcium Carbonate', dose: '600 mg', route: 'PO', frequency: 'BID', start_date: '2023-06-01', indication: 'Supplement', status: 'Home Med — Active', ordered_by: 'PCP' },
  { name: 'Multivitamin', dose: '1 tab', route: 'PO', frequency: 'Daily', start_date: '2020-01-01', indication: 'Supplement', status: 'Home Med — Active', ordered_by: 'PCP' },
  { name: 'Docusate Sodium', dose: '100 mg', route: 'PO', frequency: 'BID', start_date: '2026-02-23', indication: 'Bowel regimen', status: 'Active', ordered_by: 'Dr. Sarah Mitchell' },
  { name: 'Sennosides', dose: '8.6 mg', route: 'PO', frequency: 'Daily PRN', start_date: '2026-02-23', indication: 'Constipation', status: 'Active', ordered_by: 'Dr. Sarah Mitchell' },
  { name: 'Acetaminophen', dose: '650 mg', route: 'PO', frequency: 'Q6H PRN', start_date: '2026-02-23', indication: 'Pain/Fever', status: 'Active', ordered_by: 'Dr. Sarah Mitchell' },
  { name: 'Insulin Lispro', dose: 'Sliding scale', route: 'SubQ', frequency: 'AC + HS', start_date: '2026-02-23', indication: 'Hyperglycemia', status: 'Active', ordered_by: 'Dr. Kevin Zhao' },
]

const ADDITIONAL_NOTES = [
  {
    type: 'H&P',
    author: 'Dr. Kevin Zhao, PGY-2, Internal Medicine',
    timestamp: '2026-02-23T08:00:00',
    title: 'History and Physical — Pre-operative Evaluation',
    content: `CHIEF COMPLAINT: Right knee pain, scheduled for TKA.

HPI: 67M with severe right knee OA presenting for scheduled R TKA. Has failed conservative management including PT, NSAIDs, corticosteroid injections x3. Last injection 6 months ago with minimal relief. Pain 7/10 at rest, 9/10 with activity. Ambulates with cane. Unable to climb stairs.

PMH: HTN (controlled on lisinopril), T2DM (controlled on metformin, A1c 7.1%), Hyperlipidemia, BPH, History of DVT L LE 2023 (completed anticoagulation), History of HIT 2023.

PSH: Appendectomy (1995), L inguinal hernia repair (2010)

MEDICATIONS: [see medication list]

ALLERGIES: Penicillin (rash), Sulfa (rash), Contrast dye (anaphylaxis)

ROS: Constitutional: fatigue. CV: no chest pain, no palpitations. Pulm: no SOB, no cough. GI: no N/V/D, no melena. MSK: R knee pain as above.

EXAM: Alert, oriented, NAD. CV: RRR, no murmurs. Lungs: CTAB. Abdomen: soft, NT, ND. Ext: R knee with crepitus, limited ROM 0-100 deg, stable ligaments. L LE: no edema, no calf tenderness.

ASSESSMENT/PLAN:
1. R knee OA — proceed with TKA per Dr. Mitchell
2. DVT prophylaxis — per ortho protocol
3. DM — hold metformin day of surgery, sliding scale insulin
4. HTN — continue lisinopril
5. Code status: Full code`
  },
  {
    type: 'Anesthesia Note',
    author: 'Dr. Robert Kim, MD, Anesthesiology',
    timestamp: '2026-02-23T11:30:00',
    title: 'Pre-Anesthesia Evaluation',
    content: `ASA Class: III
Airway: Mallampati II, adequate mouth opening, no anticipated difficulty
Plan: Spinal anesthesia with sedation
NPO Status: Confirmed NPO since midnight
Consents: Signed and witnessed
Allergies reviewed: PCN, Sulfa, Contrast dye
Labs reviewed: BMP, CBC within normal limits. Type and screen on file.
EKG: NSR, no acute changes
CXR: Clear

INTRAOPERATIVE: Spinal placed L3-4, adequate block achieved. Midazolam 2mg IV for sedation. Vitals stable throughout. EBL 350mL. Crystalloid 1500mL. UOP 200mL. No complications.`
  },
  {
    type: 'PT Note',
    author: 'Tom Wilson, DPT',
    timestamp: '2026-02-24T14:00:00',
    title: 'Physical Therapy — Initial Evaluation POD#1',
    content: `Patient evaluated at bedside. Alert, cooperative, motivated.

TRANSFERS: Supine to sit — moderate assist x1. Sit to stand — moderate assist x1 with front-wheeled walker (FWW).
AMBULATION: 10 feet with FWW, moderate assist x1. WBAT R LE per surgeon.
ROM: R knee — 0-45 degrees (limited by pain and swelling)
STRENGTH: R quad 3-/5, R hamstring 3/5. L LE grossly 4+/5.
PAIN: 6/10 at rest, 8/10 with activity. PCA in use.
BALANCE: Fair- static sitting, Poor+ dynamic standing.

ASSESSMENT: Patient presents with expected post-TKA functional limitations. Good rehab potential.
PLAN: Daily PT for ROM, strengthening, gait training, stair training. CPM machine ordered.
GOALS: Independent ambulation 200ft with FWW by POD#3. Independent transfers by POD#5. Stair negotiation by POD#6.`
  },
  {
    type: 'PT Note',
    author: 'Tom Wilson, DPT',
    timestamp: '2026-02-26T10:00:00',
    title: 'Physical Therapy — Progress Note POD#3',
    content: `AMBULATION: 200 feet with FWW, contact guard assist. Gait pattern improving, decreased Trendelenburg.
ROM: R knee 0-85 degrees (improved from 0-45 POD#1). Flexion gains on track.
TRANSFERS: Supine to sit — supervision. Sit to stand — supervision with FWW.
STAIRS: Not yet attempted.
PAIN: 4/10 at rest, 6/10 with PT. Decreasing PCA use.
CPM: Tolerated to 90 degrees.

Patient meeting goals on schedule. Continue daily PT.`
  },
  {
    type: 'PT Note',
    author: 'Tom Wilson, DPT',
    timestamp: '2026-02-28T10:00:00',
    title: 'Physical Therapy — Progress Note POD#5',
    content: `AMBULATION: 400 feet with FWW, independent. Gait pattern near-normal with device.
ROM: R knee 0-95 degrees. Good flexion progression.
TRANSFERS: Independent all surfaces.
STAIRS: 12 steps up/down with rail, step-over-step ascending, step-to pattern descending. Supervision.
PAIN: 2/10 at rest, 4/10 with activity. Transitioned off PCA to oral PRN.
BALANCE: Good static and dynamic standing.

Patient has met discharge goals. Recommend home PT 2-3x/week. DC planning in progress.
NOTE: Patient appeared more fatigued today than prior sessions. Paler complexion noted. Vital signs stable per nursing.`
  },
  {
    type: 'Dietary Note',
    author: 'Nutritional Services',
    timestamp: '2026-02-24T11:00:00',
    title: 'Dietary Consultation — Post-operative',
    content: `Diet: Regular, Cardiac/Diabetic
Caloric needs: ~2000 kcal/day
Protein goal: 80-100g/day for wound healing
Current intake: ~50% of meals (decreased appetite post-op, nausea POD#0-1)
Weight: 83.5 kg (up from 82.0 pre-op, expected with IV fluids)
Blood glucose management: Sliding scale insulin ordered, monitoring AC+HS
Recommendations:
- Encourage oral intake, high-protein supplements between meals
- Continue diabetic diet with carb-consistent meals
- Monitor weight daily
- Reassess in 3 days or as needed`
  },
]

const NOISE_LABS_EXTRA = {
  'Pre-operative': { chloride: { value: 102, unit: 'mEq/L', ref: '98-106', flag: '' }, co2: { value: 24, unit: 'mEq/L', ref: '22-29', flag: '' }, calcium: { value: 9.4, unit: 'mg/dL', ref: '8.5-10.5', flag: '' }, albumin: { value: 3.8, unit: 'g/dL', ref: '3.5-5.5', flag: '' }, total_protein: { value: 7.0, unit: 'g/dL', ref: '6.0-8.3', flag: '' }, ast: { value: 22, unit: 'U/L', ref: '10-40', flag: '' }, alt: { value: 18, unit: 'U/L', ref: '7-56', flag: '' }, alk_phos: { value: 78, unit: 'U/L', ref: '44-147', flag: '' }, total_bili: { value: 0.8, unit: 'mg/dL', ref: '0.1-1.2', flag: '' }, magnesium: { value: 2.0, unit: 'mg/dL', ref: '1.7-2.2', flag: '' }, phosphorus: { value: 3.5, unit: 'mg/dL', ref: '2.5-4.5', flag: '' } },
  'POD#6 (Today — 06:00)': { chloride: { value: 104, unit: 'mEq/L', ref: '98-106', flag: '' }, co2: { value: 20, unit: 'mEq/L', ref: '22-29', flag: 'L' }, calcium: { value: 8.1, unit: 'mg/dL', ref: '8.5-10.5', flag: 'L' }, albumin: { value: 2.9, unit: 'g/dL', ref: '3.5-5.5', flag: 'L' }, ldh: { value: 340, unit: 'U/L', ref: '140-280', flag: 'H' }, magnesium: { value: 1.6, unit: 'mg/dL', ref: '1.7-2.2', flag: 'L' }, phosphorus: { value: 2.2, unit: 'mg/dL', ref: '2.5-4.5', flag: 'L' } },
}


/* ════════════════════════════════════════════════════════════════════
   HELPER FUNCTIONS
   ════════════════════════════════════════════════════════════════════ */

function fmtDate(ts) {
  const d = new Date(ts)
  return d.toLocaleDateString('en-US', { month: '2-digit', day: '2-digit', year: '2-digit' })
}

function fmtDateTime(ts) {
  const d = new Date(ts)
  return d.toLocaleDateString('en-US', { month: '2-digit', day: '2-digit' }) + ' ' +
    d.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', hour12: false })
}

function flagClass(flag) {
  if (!flag) return ''
  const f = flag.toLowerCase()
  if (f.includes('critical')) return 'emr-flag-critical'
  if (f === 'high' || f === 'h') return 'emr-flag-high'
  if (f === 'low' || f === 'l') return 'emr-flag-low'
  if (f.includes('high')) return 'emr-flag-high'
  if (f.includes('low')) return 'emr-flag-low'
  return ''
}

function flagLabel(flag) {
  if (!flag || flag === 'Normal') return ''
  const f = flag.toLowerCase()
  if (f.includes('critical low')) return 'CL'
  if (f.includes('critical high')) return 'CH'
  if (f.includes('critical')) return 'C'
  if (f.includes('borderline')) return '*'
  if (f === 'high' || f === 'h' || f.includes('high')) return 'H'
  if (f === 'low' || f === 'l' || f.includes('low')) return 'L'
  return ''
}


/* ════════════════════════════════════════════════════════════════════
   EMR PATIENT HEADER (Epic-style blue bar)
   ════════════════════════════════════════════════════════════════════ */

function EMRHeader({ patient }) {
  const d = patient.demographics
  const emrAllergies = (patient.allergies || []).filter(a => a.allergen !== 'Heparin')

  return (
    <div className="emr-header">
      <div className="emr-header-left">
        <div className="emr-header-photo">
          <div className="emr-avatar">{d.name.split(' ').map(n => n[0]).join('')}</div>
        </div>
        <div className="emr-header-info">
          <div className="emr-patient-name">{d.name}</div>
          <div className="emr-patient-details">
            <span>MRN: {d.mrn}</span>
            <span className="emr-sep">|</span>
            <span>DOB: {d.dob} ({d.age}yo)</span>
            <span className="emr-sep">|</span>
            <span>{d.sex}</span>
            <span className="emr-sep">|</span>
            <span className="emr-room-badge">Room {d.room}{d.bed}</span>
            <span className="emr-sep">|</span>
            <span>Admitted: {d.admission_date}</span>
            <span className="emr-sep">|</span>
            <span>{d.attending}</span>
          </div>
        </div>
      </div>
      <div className="emr-header-right">
        <div className="emr-code-status">{d.code_status}</div>
        <div className="emr-header-allergies">
          <span className="emr-allergy-label">ALLERGIES:</span>
          {emrAllergies.map((a, i) => (
            <span key={i} className="emr-allergy-tag" title={a.reaction}>
              {a.allergen} ({a.reaction.split('(')[0].split('—')[0].trim()})
            </span>
          ))}
        </div>
      </div>
    </div>
  )
}


/* ════════════════════════════════════════════════════════════════════
   TAB: SUMMARY / DASHBOARD
   ════════════════════════════════════════════════════════════════════ */

function SummaryTab({ patient }) {
  const vitals = patient.vitals?.trend || []
  const lastVitals = vitals[vitals.length - 1] || {}
  const problems = patient.problem_list || []
  const meds = patient.current_medications || []
  const orders = patient.orders || []

  return (
    <div className="emr-summary-grid">
      {/* Left column */}
      <div className="emr-summary-left">
        {/* Recent Vitals */}
        <div className="emr-card">
          <div className="emr-card-header">
            Recent Vitals
            <span className="emr-updated">Last updated: 03/01/2026 13:30</span>
          </div>
          <table className="emr-table">
            <thead>
              <tr>
                <th>Time</th><th>BP</th><th>HR</th><th>RR</th><th>SpO2</th><th>Temp</th>
              </tr>
            </thead>
            <tbody>
              {TODAY_VITALS.slice(-5).map((v, i) => (
                <tr key={i}>
                  <td>{v.time}</td>
                  <td className={parseInt(v.bp) < 90 ? 'emr-flag-critical' : ''}>{v.bp}</td>
                  <td className={v.hr > 100 ? 'emr-flag-high' : ''}>{v.hr}</td>
                  <td className={v.rr > 20 ? 'emr-flag-high' : ''}>{v.rr}</td>
                  <td className={v.spo2 < 95 ? 'emr-flag-low' : ''}>{v.spo2}%</td>
                  <td className={v.temp >= 38.0 ? 'emr-flag-high' : ''}>{v.temp}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Active Problems */}
        <div className="emr-card">
          <div className="emr-card-header">Active Problem List</div>
          <div className="emr-list">
            {problems.map((p, i) => (
              <div key={i} className="emr-list-row">
                <span className="emr-list-bullet">{i + 1}.</span>
                <span className={p.status.includes('Historical') ? 'emr-text-muted' : ''}>
                  {p.problem.split('—')[0].trim()}
                </span>
                <span className="emr-list-status">[{p.status.split('—')[0].trim()}]</span>
                <span className="emr-list-icd">{p.icd10}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Todo / Reminders */}
        <div className="emr-card">
          <div className="emr-card-header">
            Tasks / Reminders
            <span className="emr-badge-count">4</span>
          </div>
          <div className="emr-list">
            <div className="emr-todo-row"><input type="checkbox" disabled /> <span>Review AM labs — Hgb critical low</span> <span className="emr-todo-priority emr-todo-stat">STAT</span></div>
            <div className="emr-todo-row"><input type="checkbox" disabled /> <span>Discharge planning — SW/CM follow-up</span> <span className="emr-todo-priority">Routine</span></div>
            <div className="emr-todo-row"><input type="checkbox" disabled /> <span>Warfarin transition — pharmacy consult</span> <span className="emr-todo-priority">Routine</span></div>
            <div className="emr-todo-row"><input type="checkbox" disabled checked /> <span>PT eval complete — cleared for stairs</span> <span className="emr-todo-priority">Done</span></div>
          </div>
        </div>
      </div>

      {/* Right column */}
      <div className="emr-summary-right">
        {/* Key Labs */}
        <div className="emr-card">
          <div className="emr-card-header">
            Key Lab Values — Today 06:00
            <span className="emr-updated">Verified by Lab 06:45</span>
          </div>
          <table className="emr-table">
            <thead><tr><th>Test</th><th>Value</th><th>Ref Range</th><th>Flag</th></tr></thead>
            <tbody>
              <tr><td>Hgb</td><td className="emr-flag-critical">8.2 g/dL</td><td>13.5-17.5</td><td className="emr-flag-critical">CL</td></tr>
              <tr><td>Hct</td><td className="emr-flag-critical">24.6%</td><td>38.3-48.6</td><td className="emr-flag-critical">CL</td></tr>
              <tr><td>Plt</td><td className="emr-flag-critical">89 K/uL</td><td>150-400</td><td className="emr-flag-critical">CL</td></tr>
              <tr><td>WBC</td><td className="emr-flag-high">12.1 K/uL</td><td>4.5-11.0</td><td className="emr-flag-high">H</td></tr>
              <tr><td>BUN</td><td className="emr-flag-high">34 mg/dL</td><td>7-20</td><td className="emr-flag-high">H</td></tr>
              <tr><td>Cr</td><td>1.3 mg/dL</td><td>0.7-1.3</td><td style={{color:'#b45309'}}>*</td></tr>
              <tr><td>Lactate</td><td className="emr-flag-high">2.8 mmol/L</td><td>0.5-2.0</td><td className="emr-flag-high">H</td></tr>
              <tr><td>aPTT</td><td className="emr-flag-critical">98 sec</td><td>60-80</td><td className="emr-flag-critical">CH</td></tr>
            </tbody>
          </table>
        </div>

        {/* Active Medications count */}
        <div className="emr-card">
          <div className="emr-card-header">
            Medications Summary
            <span className="emr-badge-count">{meds.filter(m => m.status.startsWith('Active')).length + EXTRA_MEDICATIONS.filter(m => m.status.includes('Active')).length}</span>
          </div>
          <div className="emr-list">
            <div className="emr-list-row"><span>Active Medications: {meds.filter(m => m.status.startsWith('Active') || m.status === 'Active').length}</span></div>
            <div className="emr-list-row"><span>Home Medications: {EXTRA_MEDICATIONS.length}</span></div>
            <div className="emr-list-row"><span>High-alert: Heparin drip, Morphine PCA, Insulin</span></div>
            <div className="emr-list-row emr-text-muted"><span>Last reconciled: 02/23/2026 by Dr. Zhao</span></div>
          </div>
        </div>

        {/* Active Orders count */}
        <div className="emr-card">
          <div className="emr-card-header">
            Active Orders
            <span className="emr-badge-count">{orders.filter(o => o.status === 'Active' || o.status === 'Ordered').length}</span>
          </div>
          <div className="emr-list">
            {orders.filter(o => o.status === 'Active' || o.status === 'Ordered' || o.status === 'Pending').slice(0, 5).map((o, i) => (
              <div key={i} className="emr-list-row">
                <span className={`emr-order-status emr-order-${o.status.toLowerCase()}`}>{o.status}</span>
                <span>{o.order}</span>
              </div>
            ))}
            <div className="emr-list-row emr-text-muted">+ {orders.filter(o => o.status === 'Active').length - 5 > 0 ? orders.filter(o => o.status === 'Active').length - 5 : 0} more active orders...</div>
          </div>
        </div>

        {/* Weights */}
        <div className="emr-card">
          <div className="emr-card-header">Daily Weights</div>
          <table className="emr-table emr-table-compact">
            <thead><tr><th>Date</th><th>Weight (kg)</th><th>Change</th></tr></thead>
            <tbody>
              {(patient.noise_data?.daily_weights || []).map((w, i, arr) => (
                <tr key={i}>
                  <td>{w.date}</td>
                  <td>{w.weight_kg}</td>
                  <td className="emr-text-muted">{i > 0 ? (w.weight_kg - arr[i-1].weight_kg > 0 ? '+' : '') + (w.weight_kg - arr[i-1].weight_kg).toFixed(1) : '—'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}


/* ════════════════════════════════════════════════════════════════════
   TAB: VITALS (Dense wall of numbers)
   ════════════════════════════════════════════════════════════════════ */

function VitalsTab({ patient }) {
  const allVitals = [...HISTORICAL_VITALS, ...TODAY_VITALS]

  return (
    <div>
      <div className="emr-card">
        <div className="emr-card-header">
          Vital Signs — All Recordings
          <span className="emr-updated">Frequency: Q4H (increased to Q1H 03/01 13:00)</span>
          <button className="emr-btn-sm">Print</button>
          <button className="emr-btn-sm">Graph View</button>
        </div>
        <div className="emr-table-scroll">
          <table className="emr-table emr-table-vitals">
            <thead>
              <tr>
                <th>Date</th>
                <th>Time</th>
                <th>Label</th>
                <th>BP (mmHg)</th>
                <th>HR (bpm)</th>
                <th>RR (/min)</th>
                <th>SpO2 (%)</th>
                <th>Temp (°C)</th>
                <th>Pain (0-10)</th>
              </tr>
            </thead>
            <tbody>
              {allVitals.map((v, i) => {
                const bpSys = parseInt(v.bp.split('/')[0])
                const isCritical = bpSys < 90 || v.hr > 110
                return (
                  <tr key={i} className={isCritical ? 'emr-row-critical' : ''}>
                    <td>{v.date}</td>
                    <td>{v.time}</td>
                    <td className="emr-text-muted">{v.label}</td>
                    <td className={bpSys < 90 ? 'emr-flag-critical' : bpSys < 100 ? 'emr-flag-low' : ''}>{v.bp}</td>
                    <td className={v.hr > 100 ? 'emr-flag-high' : ''}>{v.hr}</td>
                    <td className={v.rr > 20 ? 'emr-flag-high' : ''}>{v.rr}</td>
                    <td className={v.spo2 < 95 ? 'emr-flag-low' : ''}>{v.spo2}</td>
                    <td className={v.temp >= 38.0 ? 'emr-flag-high' : ''}>{v.temp.toFixed(1)}</td>
                    <td>{v.pain}</td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}


/* ════════════════════════════════════════════════════════════════════
   TAB: LABS / RESULTS
   ════════════════════════════════════════════════════════════════════ */

function LabsTab({ patient }) {
  const [openSection, setOpenSection] = useState('chemistry')
  const timestamps = patient.labs?.timestamps || []
  const labels = timestamps.map(t => t.label)

  const getVal = (tIdx, analyte) => {
    const r = timestamps[tIdx]?.results?.[analyte]
    if (!r) return { display: '', flag: '' }
    return { display: `${r.value} ${r.unit || ''}`.trim(), flag: r.flag || '', note: r.note }
  }

  const chemRows = [
    { name: 'sodium', label: 'Sodium', ref: '136-145 mEq/L' },
    { name: 'potassium', label: 'Potassium', ref: '3.5-5.0 mEq/L' },
    { name: 'chloride', label: 'Chloride', ref: '98-106 mEq/L' },
    { name: 'co2', label: 'CO2', ref: '22-29 mEq/L' },
    { name: 'bun', label: 'BUN', ref: '7-20 mg/dL' },
    { name: 'creatinine', label: 'Creatinine', ref: '0.7-1.3 mg/dL' },
    { name: 'glucose', label: 'Glucose', ref: '70-100 mg/dL' },
    { name: 'calcium', label: 'Calcium', ref: '8.5-10.5 mg/dL' },
  ]

  const cbcRows = [
    { name: 'wbc', label: 'WBC', ref: '4.5-11.0 K/uL' },
    { name: 'hemoglobin', label: 'Hemoglobin', ref: '13.5-17.5 g/dL' },
    { name: 'hematocrit', label: 'Hematocrit', ref: '38.3-48.6 %' },
    { name: 'platelets', label: 'Platelets', ref: '150-400 K/uL' },
  ]

  const coagRows = [
    { name: 'pt', label: 'PT', ref: '11-13.5 sec' },
    { name: 'inr', label: 'INR', ref: '0.8-1.2' },
    { name: 'aptt', label: 'aPTT', ref: '25-35 sec' },
  ]

  const miscRows = [
    { name: 'lactate', label: 'Lactate', ref: '0.5-2.0 mmol/L' },
    { name: 'd_dimer', label: 'D-Dimer', ref: '<0.5 ug/mL' },
    { name: 'fibrinogen', label: 'Fibrinogen', ref: '200-400 mg/dL' },
    { name: 'troponin', label: 'Troponin', ref: '<0.04 ng/mL' },
    { name: 'pro_bnp', label: 'Pro-BNP', ref: '<300 pg/mL' },
  ]

  const sections = [
    { id: 'chemistry', label: 'Chemistry (BMP)', rows: chemRows },
    { id: 'hematology', label: 'Hematology (CBC)', rows: cbcRows },
    { id: 'coagulation', label: 'Coagulation', rows: coagRows },
    { id: 'miscellaneous', label: 'Miscellaneous', rows: miscRows },
    { id: 'urinalysis', label: 'Urinalysis', rows: null },
  ]

  const renderLabTable = (rows) => (
    <div className="emr-table-scroll">
      <table className="emr-table emr-table-labs">
        <thead>
          <tr>
            <th className="emr-th-sticky">Test</th>
            <th className="emr-th-sticky">Ref Range</th>
            {labels.map((l, i) => <th key={i}>{l}</th>)}
          </tr>
        </thead>
        <tbody>
          {rows.map((row, ri) => (
            <tr key={ri}>
              <td className="emr-lab-name">{row.label}</td>
              <td className="emr-text-muted emr-lab-ref">{row.ref}</td>
              {timestamps.map((_, ti) => {
                const { display, flag, note } = getVal(ti, row.name)
                // Check noise data for extra values
                const label = timestamps[ti].label
                const noiseEntry = NOISE_LABS_EXTRA[label]?.[row.name]
                const finalDisplay = display || (noiseEntry ? `${noiseEntry.value} ${noiseEntry.unit}` : '')
                const finalFlag = flag || noiseEntry?.flag || ''
                return (
                  <td key={ti} className={flagClass(finalFlag)} title={note || ''}>
                    {finalDisplay}
                    {finalFlag && flagLabel(finalFlag) ? <sup className={flagClass(finalFlag)}> {flagLabel(finalFlag)}</sup> : ''}
                  </td>
                )
              })}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )

  const renderUrinalysis = () => {
    const uas = patient.noise_data?.urinalysis || []
    return (
      <table className="emr-table">
        <thead>
          <tr>
            <th>Test</th>
            {uas.map((u, i) => <th key={i}>{u.date}</th>)}
          </tr>
        </thead>
        <tbody>
          {['color', 'clarity', 'ph', 'specific_gravity', 'protein', 'glucose', 'blood', 'leukocytes', 'nitrites'].map(field => (
            <tr key={field}>
              <td className="emr-lab-name">{field.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase())}</td>
              {uas.map((u, i) => {
                const val = u[field]
                const isAbnormal = (field === 'protein' && val !== 'Neg') || (field === 'glucose' && val !== 'Neg')
                return <td key={i} className={isAbnormal ? 'emr-flag-high' : ''}>{val}</td>
              })}
            </tr>
          ))}
        </tbody>
      </table>
    )
  }

  return (
    <div>
      <div className="emr-card">
        <div className="emr-card-header">
          Laboratory Results
          <button className="emr-btn-sm">Print</button>
          <button className="emr-btn-sm">Trend View</button>
          <button className="emr-btn-sm">Cumulative</button>
        </div>
        <div className="emr-lab-sections">
          {sections.map(sec => (
            <div key={sec.id} className="emr-lab-section">
              <div
                className={`emr-lab-section-header ${openSection === sec.id ? 'emr-lab-section-open' : ''}`}
                onClick={() => setOpenSection(openSection === sec.id ? '' : sec.id)}
              >
                <span className="emr-accordion-arrow">{openSection === sec.id ? '▼' : '▶'}</span>
                {sec.label}
              </div>
              {openSection === sec.id && (
                <div className="emr-lab-section-body">
                  {sec.rows ? renderLabTable(sec.rows) : renderUrinalysis()}
                </div>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Blood Glucose Log */}
      <div className="emr-card" style={{ marginTop: 8 }}>
        <div className="emr-card-header">Blood Glucose Log (AC + HS)</div>
        <table className="emr-table emr-table-compact">
          <thead><tr><th>Date</th><th>Time</th><th>Value (mg/dL)</th><th>Note</th></tr></thead>
          <tbody>
            {(patient.noise_data?.blood_glucose || []).map((g, i) => (
              <tr key={i}>
                <td>{g.date}</td>
                <td>{g.time}</td>
                <td className={g.value > 180 ? 'emr-flag-high' : g.value > 140 ? 'emr-flag-high' : ''}>{g.value}{g.value > 140 ? <sup className="emr-flag-high"> H</sup> : ''}</td>
                <td className="emr-text-muted">{g.note}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* I&O Records */}
      <div className="emr-card" style={{ marginTop: 8 }}>
        <div className="emr-card-header">Intake & Output Summary</div>
        <table className="emr-table emr-table-compact">
          <thead><tr><th>Date</th><th>Intake (mL)</th><th>Output (mL)</th><th>Net (mL)</th><th>Note</th></tr></thead>
          <tbody>
            {(patient.noise_data?.io_records || []).map((io, i) => (
              <tr key={i}>
                <td>{io.date}</td>
                <td>{io.intake_ml}</td>
                <td>{io.output_ml}</td>
                <td className={io.net > 500 ? 'emr-flag-high' : ''}>{io.net > 0 ? '+' : ''}{io.net}</td>
                <td className="emr-text-muted">{io.note || ''}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}


/* ════════════════════════════════════════════════════════════════════
   TAB: MEDICATIONS
   ════════════════════════════════════════════════════════════════════ */

function MedicationsTab({ patient }) {
  const [sortBy, setSortBy] = useState('name')
  const patientMeds = patient.current_medications || []
  const allMeds = [...patientMeds, ...EXTRA_MEDICATIONS]

  const sorted = useMemo(() => {
    const arr = [...allMeds]
    if (sortBy === 'name') arr.sort((a, b) => a.name.localeCompare(b.name))
    if (sortBy === 'route') arr.sort((a, b) => a.route.localeCompare(b.route))
    if (sortBy === 'status') arr.sort((a, b) => a.status.localeCompare(b.status))
    return arr
  }, [allMeds, sortBy])

  return (
    <div>
      <div className="emr-card">
        <div className="emr-card-header">
          Medication Administration Record (MAR)
          <span className="emr-updated">Reconciled: 02/23/2026 — Dr. Kevin Zhao</span>
          <button className="emr-btn-sm">Print</button>
          <button className="emr-btn-sm">Reconcile</button>
          <button className="emr-btn-sm">+ New Order</button>
        </div>
        <div className="emr-sort-bar">
          Sort by:
          <button className={`emr-sort-btn ${sortBy === 'name' ? 'emr-sort-active' : ''}`} onClick={() => setSortBy('name')}>Name</button>
          <button className={`emr-sort-btn ${sortBy === 'route' ? 'emr-sort-active' : ''}`} onClick={() => setSortBy('route')}>Route</button>
          <button className={`emr-sort-btn ${sortBy === 'status' ? 'emr-sort-active' : ''}`} onClick={() => setSortBy('status')}>Status</button>
        </div>
        <table className="emr-table">
          <thead>
            <tr>
              <th>Medication</th>
              <th>Dose</th>
              <th>Route</th>
              <th>Frequency</th>
              <th>Start Date</th>
              <th>Indication</th>
              <th>Ordered By</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            {sorted.map((med, i) => (
              <tr key={i} className={med.status === 'Completed' ? 'emr-row-inactive' : ''}>
                <td className="emr-med-name">{med.name}</td>
                <td>{med.dose}</td>
                <td>{med.route}</td>
                <td>{med.frequency}</td>
                <td>{med.start_date}</td>
                <td className="emr-text-muted">{med.indication}</td>
                <td className="emr-text-muted">{med.ordered_by || '—'}</td>
                <td>
                  <span className={`emr-med-status ${med.status.includes('Home') ? 'emr-med-home' : med.status === 'Completed' ? 'emr-med-completed' : 'emr-med-active'}`}>
                    {med.status}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}


/* ════════════════════════════════════════════════════════════════════
   TAB: NOTES (with buried HIT history — 3+ clicks deep)
   ════════════════════════════════════════════════════════════════════ */

function NotesTab({ patient }) {
  const [view, setView] = useState('current')
  const [expandedNote, setExpandedNote] = useState(null)
  const [showEncounterNotes, setShowEncounterNotes] = useState(false)

  const allNotes = [...(patient.clinical_notes || []), ...ADDITIONAL_NOTES]
  const admissionDate = new Date('2026-02-23')

  const currentNotes = allNotes
    .filter(n => new Date(n.timestamp) >= admissionDate)
    .sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp))

  const historicalNotes = allNotes
    .filter(n => new Date(n.timestamp) < admissionDate)
    .sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp))

  const noteTypeIcon = (type) => {
    switch (type) {
      case 'Progress Note': return '[PN]'
      case 'Nursing Note': return '[NN]'
      case 'Surgical Note': return '[OP]'
      case 'H&P': return '[HP]'
      case 'Anesthesia Note': return '[AN]'
      case 'PT Note': return '[PT]'
      case 'Dietary Note': return '[DT]'
      case 'Discharge Summary': return '[DS]'
      default: return '[--]'
    }
  }

  if (view === 'current') {
    return (
      <div>
        <div className="emr-card">
          <div className="emr-card-header">
            Clinical Notes — Current Encounter
            <span className="emr-updated">Admission: 02/23/2026</span>
            <button className="emr-btn-sm">Print All</button>
            <button className="emr-btn-sm">+ Add Note</button>
          </div>
          <div className="emr-notes-list">
            {currentNotes.map((note, i) => (
              <div key={i} className="emr-note-item">
                <div
                  className="emr-note-row"
                  onClick={() => setExpandedNote(expandedNote === i ? null : i)}
                >
                  <span className="emr-note-type">{noteTypeIcon(note.type)}</span>
                  <span className="emr-note-date">{fmtDateTime(note.timestamp)}</span>
                  <span className="emr-note-title">{note.title}</span>
                  <span className="emr-note-author">{note.author}</span>
                  <span className="emr-note-expand">{expandedNote === i ? '▼' : '▶'}</span>
                </div>
                {expandedNote === i && (
                  <div className="emr-note-content">
                    <div className="emr-note-meta">
                      <span>Type: {note.type}</span>
                      <span>Author: {note.author}</span>
                      <span>Signed: {fmtDateTime(note.timestamp)}</span>
                      <span>Status: Signed</span>
                    </div>
                    <pre className="emr-note-text">{note.content}</pre>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Previous Encounters — collapsed, requires click to open */}
        <div className="emr-card" style={{ marginTop: 8 }}>
          <div
            className="emr-card-header emr-clickable"
            onClick={() => setView('encounters')}
          >
            <span className="emr-accordion-arrow">▶</span>
            Previous Encounters
            <span className="emr-badge-count">{historicalNotes.length > 0 ? '1 encounter' : '0'}</span>
            <span className="emr-text-muted" style={{ marginLeft: 'auto', fontSize: 10 }}>Click to view historical records</span>
          </div>
        </div>
      </div>
    )
  }

  if (view === 'encounters') {
    return (
      <div>
        <div className="emr-card">
          <div className="emr-card-header">
            <span className="emr-back-link" onClick={() => setView('current')}>← Back to Current Notes</span>
            Previous Encounters
          </div>
          <div className="emr-encounter-list">
            <div
              className="emr-encounter-row emr-clickable"
              onClick={() => { setShowEncounterNotes(true); setView('encounter_detail') }}
            >
              <div className="emr-encounter-info">
                <span className="emr-encounter-dates">Oct 28, 2023 — Nov 20, 2023</span>
                <span className="emr-encounter-service">Hematology — Dr. James Park</span>
                <span className="emr-encounter-dx">DVT, Left Lower Extremity; Heparin-Induced Thrombocytopenia</span>
              </div>
              <span className="emr-note-expand">▶</span>
            </div>
          </div>
        </div>
      </div>
    )
  }

  if (view === 'encounter_detail') {
    return (
      <div>
        <div className="emr-card">
          <div className="emr-card-header">
            <span className="emr-back-link" onClick={() => setView('encounters')}>← Back to Encounters</span>
            Encounter: Oct 28 — Nov 20, 2023 | Hematology
          </div>
          <div className="emr-notes-list">
            {historicalNotes.map((note, i) => (
              <div key={i} className="emr-note-item">
                <div
                  className="emr-note-row"
                  onClick={() => setExpandedNote(expandedNote === `hist-${i}` ? null : `hist-${i}`)}
                >
                  <span className="emr-note-type">{noteTypeIcon(note.type)}</span>
                  <span className="emr-note-date">{fmtDateTime(note.timestamp)}</span>
                  <span className="emr-note-title">{note.title}</span>
                  <span className="emr-note-author">{note.author}</span>
                  <span className="emr-note-expand">{expandedNote === `hist-${i}` ? '▼' : '▶'}</span>
                </div>
                {expandedNote === `hist-${i}` && (
                  <div className="emr-note-content">
                    <div className="emr-note-meta">
                      <span>Type: {note.type}</span>
                      <span>Author: {note.author}</span>
                      <span>Signed: {fmtDateTime(note.timestamp)}</span>
                    </div>
                    <pre className="emr-note-text">{note.content}</pre>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      </div>
    )
  }

  return null
}


/* ════════════════════════════════════════════════════════════════════
   TAB: IMAGING
   ════════════════════════════════════════════════════════════════════ */

function ImagingTab({ patient }) {
  const [expandedStudy, setExpandedStudy] = useState(null)
  const studies = patient.imaging || []

  return (
    <div>
      <div className="emr-card">
        <div className="emr-card-header">
          Imaging Studies
          <button className="emr-btn-sm">Print</button>
        </div>
        <table className="emr-table">
          <thead>
            <tr><th>Date</th><th>Type</th><th>Study</th><th>Status</th><th>Read By</th></tr>
          </thead>
          <tbody>
            {studies.map((s, i) => (
              <React.Fragment key={i}>
                <tr className="emr-clickable" onClick={() => setExpandedStudy(expandedStudy === i ? null : i)}>
                  <td>{fmtDate(s.timestamp)}</td>
                  <td>{s.type}</td>
                  <td>{s.study}</td>
                  <td><span className="emr-imaging-final">Final</span></td>
                  <td className="emr-text-muted">{s.read_by}</td>
                </tr>
                {expandedStudy === i && (
                  <tr className="emr-imaging-detail">
                    <td colSpan={5}>
                      <div className="emr-imaging-report">
                        <strong>REPORT:</strong>
                        <p>{s.result}</p>
                      </div>
                    </td>
                  </tr>
                )}
              </React.Fragment>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}


/* ════════════════════════════════════════════════════════════════════
   TAB: ALLERGIES (NO Heparin — this is the deliberate gap)
   ════════════════════════════════════════════════════════════════════ */

function AllergiesTab({ patient }) {
  // CRITICAL: Filter out Heparin allergy — this simulates the real-world error
  // where the HIT allergy wasn't properly transferred from the 2023 admission
  const emrAllergies = (patient.allergies || []).filter(a => a.allergen !== 'Heparin')

  return (
    <div>
      <div className="emr-card">
        <div className="emr-card-header">
          Allergies / Adverse Reactions
          <span className="emr-updated">Last reviewed: 02/23/2026 by Dr. Kevin Zhao</span>
          <button className="emr-btn-sm">+ Add Allergy</button>
        </div>
        <table className="emr-table">
          <thead>
            <tr>
              <th>Allergen</th>
              <th>Reaction</th>
              <th>Severity</th>
              <th>Verified</th>
              <th>Documented</th>
            </tr>
          </thead>
          <tbody>
            {emrAllergies.map((a, i) => (
              <tr key={i}>
                <td className={a.severity?.includes('Severe') ? 'emr-flag-critical' : 'emr-allergy-name'}>
                  {a.allergen}
                </td>
                <td>{a.reaction}</td>
                <td>
                  <span className={`emr-severity-badge ${a.severity?.includes('Severe') ? 'emr-severity-severe' : 'emr-severity-moderate'}`}>
                    {a.severity}
                  </span>
                </td>
                <td>{a.verified ? 'Yes' : 'No'}</td>
                <td className="emr-text-muted">{a.documented_date || '—'}</td>
              </tr>
            ))}
          </tbody>
        </table>
        <div className="emr-allergy-footer">
          <span className="emr-text-muted">Total allergies on file: {emrAllergies.length}</span>
          <span className="emr-text-muted">NKDA: No</span>
        </div>
      </div>
    </div>
  )
}


/* ════════════════════════════════════════════════════════════════════
   TAB: PROBLEM LIST
   ════════════════════════════════════════════════════════════════════ */

function ProblemListTab({ patient }) {
  const problems = patient.problem_list || []
  const active = problems.filter(p => p.status.includes('Active'))
  const historical = problems.filter(p => !p.status.includes('Active'))

  return (
    <div>
      <div className="emr-card">
        <div className="emr-card-header">
          Problem List — Active
          <span className="emr-badge-count">{active.length}</span>
        </div>
        <table className="emr-table">
          <thead><tr><th>#</th><th>Problem</th><th>Status</th><th>ICD-10</th><th>Onset</th></tr></thead>
          <tbody>
            {active.map((p, i) => (
              <tr key={i}>
                <td>{i + 1}</td>
                <td>{p.problem}</td>
                <td>{p.status}</td>
                <td className="emr-text-muted">{p.icd10}</td>
                <td className="emr-text-muted">—</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="emr-card" style={{ marginTop: 8 }}>
        <div className="emr-card-header">
          Problem List — Historical / Resolved
          <span className="emr-badge-count">{historical.length}</span>
        </div>
        <table className="emr-table">
          <thead><tr><th>#</th><th>Problem</th><th>Status</th><th>ICD-10</th></tr></thead>
          <tbody>
            {historical.map((p, i) => (
              <tr key={i} className="emr-row-inactive">
                <td>{active.length + i + 1}</td>
                <td className="emr-text-muted">{p.problem}</td>
                <td className="emr-text-muted">{p.status}</td>
                <td className="emr-text-muted">{p.icd10}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}


/* ════════════════════════════════════════════════════════════════════
   TAB: ORDERS
   ════════════════════════════════════════════════════════════════════ */

function OrdersTab({ patient }) {
  const orders = patient.orders || []
  const active = orders.filter(o => o.status === 'Active' || o.status === 'Ordered' || o.status === 'Pending')
  const inactive = orders.filter(o => o.status === 'Completed' || o.status === 'Discontinued')

  return (
    <div>
      <div className="emr-card">
        <div className="emr-card-header">
          Active Orders
          <span className="emr-badge-count">{active.length}</span>
          <button className="emr-btn-sm">+ New Order</button>
          <button className="emr-btn-sm">Print</button>
        </div>
        <table className="emr-table">
          <thead>
            <tr><th>Order</th><th>Type</th><th>Details</th><th>Ordered By</th><th>Date</th><th>Status</th></tr>
          </thead>
          <tbody>
            {active.map((o, i) => (
              <tr key={i}>
                <td className="emr-med-name">{o.order}</td>
                <td className="emr-text-muted">{o.type}</td>
                <td className="emr-text-muted" style={{ maxWidth: 200, whiteSpace: 'normal', fontSize: 11 }}>{o.details}</td>
                <td className="emr-text-muted">{o.ordered_by}</td>
                <td>{o.date}</td>
                <td><span className={`emr-order-status emr-order-${o.status.toLowerCase()}`}>{o.status}</span></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {inactive.length > 0 && (
        <div className="emr-card" style={{ marginTop: 8 }}>
          <div className="emr-card-header">Completed / Discontinued Orders</div>
          <table className="emr-table">
            <thead>
              <tr><th>Order</th><th>Type</th><th>Details</th><th>Date</th><th>Status</th></tr>
            </thead>
            <tbody>
              {inactive.map((o, i) => (
                <tr key={i} className="emr-row-inactive">
                  <td className="emr-text-muted">{o.order}</td>
                  <td className="emr-text-muted">{o.type}</td>
                  <td className="emr-text-muted">{o.details}</td>
                  <td className="emr-text-muted">{o.date}</td>
                  <td><span className={`emr-order-status emr-order-${o.status.toLowerCase()}`}>{o.status}</span></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}


/* ════════════════════════════════════════════════════════════════════
   TAB: CARE TEAM
   ════════════════════════════════════════════════════════════════════ */

function CareTeamTab({ patient }) {
  const team = patient.care_team || []

  return (
    <div>
      <div className="emr-card">
        <div className="emr-card-header">
          Care Team — Current
          <span className="emr-updated">Room 412A, Med-Surg 4 West</span>
        </div>
        <table className="emr-table">
          <thead>
            <tr><th>Role</th><th>Name</th><th>Service</th><th>Pager</th></tr>
          </thead>
          <tbody>
            {team.map((t, i) => (
              <tr key={i}>
                <td className="emr-med-name">{t.role}</td>
                <td>{t.name}</td>
                <td className="emr-text-muted">{t.service}</td>
                <td className="emr-text-muted">{t.pager || '—'}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="emr-card" style={{ marginTop: 8 }}>
        <div className="emr-card-header">Consulting Services</div>
        <div className="emr-list">
          <div className="emr-list-row emr-text-muted">No active consults at this time.</div>
          <div className="emr-list-row emr-text-muted" style={{ fontSize: 10 }}>
            To request a consult, use the Orders tab or page the desired service.
          </div>
        </div>
      </div>
    </div>
  )
}


/* ════════════════════════════════════════════════════════════════════
   MAIN EMR VIEW COMPONENT
   ════════════════════════════════════════════════════════════════════ */

const EMR_TABS = [
  { id: 'summary', label: 'Summary' },
  { id: 'vitals', label: 'Vitals' },
  { id: 'labs', label: 'Labs / Results' },
  { id: 'medications', label: 'Medications' },
  { id: 'notes', label: 'Notes' },
  { id: 'imaging', label: 'Imaging' },
  { id: 'allergies', label: 'Allergies' },
  { id: 'problems', label: 'Problem List' },
  { id: 'orders', label: 'Orders' },
  { id: 'careteam', label: 'Care Team' },
]

export default function EMRView({ patient, onLaunchAmbient }) {
  const [activeTab, setActiveTab] = useState('summary')

  if (!patient) {
    return (
      <div className="emr-root" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <div style={{ color: '#64748b', fontSize: 14 }}>Loading patient data...</div>
      </div>
    )
  }

  return (
    <div className="emr-root">
      <EMRHeader patient={patient} />

      {/* Tab Navigation */}
      <div className="emr-tabs">
        {EMR_TABS.map(tab => (
          <div
            key={tab.id}
            className={`emr-tab ${activeTab === tab.id ? 'emr-tab-active' : ''}`}
            onClick={() => setActiveTab(tab.id)}
          >
            {tab.label}
          </div>
        ))}
      </div>

      {/* Tab Content */}
      <div className="emr-content">
        {activeTab === 'summary' && <SummaryTab patient={patient} />}
        {activeTab === 'vitals' && <VitalsTab patient={patient} />}
        {activeTab === 'labs' && <LabsTab patient={patient} />}
        {activeTab === 'medications' && <MedicationsTab patient={patient} />}
        {activeTab === 'notes' && <NotesTab patient={patient} />}
        {activeTab === 'imaging' && <ImagingTab patient={patient} />}
        {activeTab === 'allergies' && <AllergiesTab patient={patient} />}
        {activeTab === 'problems' && <ProblemListTab patient={patient} />}
        {activeTab === 'orders' && <OrdersTab patient={patient} />}
        {activeTab === 'careteam' && <CareTeamTab patient={patient} />}
      </div>

      {/* EMR footer bar */}
      <div className="emr-footer">
        <div className="emr-footer-left">
          <span>Patient: Robert Chen | MRN: MRN-2847391 | Room 412A</span>
          <span className="emr-sep">|</span>
          <span className="emr-text-muted">EHR v24.3.1 | {new Date().toLocaleTimeString()}</span>
        </div>
        <div className="emr-footer-right">
          <button className="emr-btn-sm">Messages (3)</button>
          <button className="emr-btn-sm">In Basket</button>
        </div>
      </div>

      {/* Launch Ambient Dx button — prominent floating action */}
      <button className="launch-ambient-btn" onClick={onLaunchAmbient}>
        <span className="launch-ambient-icon">◉</span>
        Launch Ambient Dx
      </button>
    </div>
  )
}
