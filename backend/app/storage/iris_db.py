"""InterSystems IRIS database layer — connection, schema, and structured clinical queries.

Connection pattern from: intersystems-community/hackmit-2024
SQL patterns from: intersystems-community/FHIR-AI-Hackathon-Kit
"""

from __future__ import annotations

from contextlib import contextmanager

from app.config import IRIS_HOST, IRIS_PORT, IRIS_NAMESPACE, IRIS_USERNAME, IRIS_PASSWORD

PATIENT_ID = "P001"


def get_connection():
    """Connect to IRIS via the native Python driver."""
    import iris
    conn_str = f"{IRIS_HOST}:{IRIS_PORT}/{IRIS_NAMESPACE}"
    return iris.connect(conn_str, IRIS_USERNAME, IRIS_PASSWORD)


@contextmanager
def get_cursor():
    """Context manager for an IRIS cursor — auto-closes connection."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        yield cursor
        conn.commit()
    finally:
        cursor.close()
        conn.close()


def test_connection() -> bool:
    """Quick health check for IRIS connectivity."""
    try:
        with get_cursor() as cur:
            cur.execute("SELECT 1")
            return cur.fetchone()[0] == 1
    except Exception as e:
        print(f"[IRIS] Connection failed: {e}")
        return False


# ─── Schema Creation ───


TABLE_DEFS = {
    "AmbientDx.Medications": """(
        patient_id VARCHAR(50),
        name VARCHAR(255),
        dose VARCHAR(255),
        route VARCHAR(50),
        frequency VARCHAR(100),
        indication VARCHAR(500),
        status VARCHAR(100),
        start_date VARCHAR(50),
        notes VARCHAR(2000)
    )""",
    "AmbientDx.Labs": """(
        patient_id VARCHAR(50),
        timepoint VARCHAR(100),
        timestamp_val VARCHAR(50),
        lab_name VARCHAR(100),
        lab_value VARCHAR(50),
        unit VARCHAR(50),
        ref_range VARCHAR(100),
        flag VARCHAR(50),
        note VARCHAR(500)
    )""",
    "AmbientDx.Allergies": """(
        patient_id VARCHAR(50),
        allergen VARCHAR(255),
        reaction VARCHAR(500),
        severity VARCHAR(100),
        documented_date VARCHAR(50),
        source_info VARCHAR(500)
    )""",
    "AmbientDx.Problems": """(
        patient_id VARCHAR(50),
        problem VARCHAR(500),
        status VARCHAR(255),
        icd10 VARCHAR(20),
        critical_flag INTEGER
    )""",
    "AmbientDx.Vitals": """(
        patient_id VARCHAR(50),
        timepoint VARCHAR(100),
        timestamp_val VARCHAR(50),
        bp_systolic INTEGER,
        bp_diastolic INTEGER,
        heart_rate INTEGER,
        resp_rate INTEGER,
        spo2 DOUBLE,
        temp DOUBLE
    )""",
}


def create_tables():
    """Create all structured AmbientDx tables (idempotent — drops first)."""
    with get_cursor() as cur:
        for table_name, definition in TABLE_DEFS.items():
            try:
                cur.execute(f"DROP TABLE {table_name}")
            except Exception:
                pass
            cur.execute(f"CREATE TABLE {table_name} {definition}")
            print(f"  [IRIS] Created {table_name}")


# ─── Data Loading ───


def load_medications(patient: dict, patient_id: str = PATIENT_ID):
    sql = (
        "INSERT INTO AmbientDx.Medications "
        "(patient_id, name, dose, route, frequency, indication, status, start_date, notes) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)"
    )
    rows = [
        (
            patient_id,
            m["name"], m["dose"], m["route"], m["frequency"],
            m["indication"], m["status"], m["start_date"], m.get("notes", ""),
        )
        for m in patient["current_medications"]
    ]
    with get_cursor() as cur:
        cur.executemany(sql, rows)
    return len(rows)


def load_allergies(patient: dict, patient_id: str = PATIENT_ID):
    sql = (
        "INSERT INTO AmbientDx.Allergies "
        "(patient_id, allergen, reaction, severity, documented_date, source_info) "
        "VALUES (?, ?, ?, ?, ?, ?)"
    )
    rows = [
        (
            patient_id,
            a["allergen"], a["reaction"], a["severity"],
            a.get("documented_date", ""), a.get("source", ""),
        )
        for a in patient["allergies"]
    ]
    with get_cursor() as cur:
        cur.executemany(sql, rows)
    return len(rows)


def load_problems(patient: dict, patient_id: str = PATIENT_ID):
    sql = (
        "INSERT INTO AmbientDx.Problems "
        "(patient_id, problem, status, icd10, critical_flag) "
        "VALUES (?, ?, ?, ?, ?)"
    )
    rows = [
        (
            patient_id,
            p["problem"], p["status"], p.get("icd10", ""),
            1 if p.get("critical_flag") else 0,
        )
        for p in patient["problem_list"]
    ]
    with get_cursor() as cur:
        cur.executemany(sql, rows)
    return len(rows)


def load_labs(patient: dict, patient_id: str = PATIENT_ID):
    sql = (
        "INSERT INTO AmbientDx.Labs "
        "(patient_id, timepoint, timestamp_val, lab_name, lab_value, unit, ref_range, flag, note) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)"
    )
    rows = []
    for tp in patient["labs"]["timestamps"]:
        for lab_name, val in tp["results"].items():
            rows.append((
                patient_id,
                tp["label"], tp["timestamp"],
                lab_name, str(val["value"]), val["unit"],
                val["ref_range"], val["flag"], val.get("note", ""),
            ))
    with get_cursor() as cur:
        cur.executemany(sql, rows)
    return len(rows)


def load_vitals(patient: dict, patient_id: str = PATIENT_ID):
    sql = (
        "INSERT INTO AmbientDx.Vitals "
        "(patient_id, timepoint, timestamp_val, bp_systolic, bp_diastolic, "
        "heart_rate, resp_rate, spo2, temp) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)"
    )
    rows = [
        (
            patient_id,
            v["label"], v["timestamp"],
            v["bp_systolic"], v["bp_diastolic"],
            v["heart_rate"], v["resp_rate"], v["spo2"], v["temp"],
        )
        for v in patient["vitals"]["trend"]
    ]
    with get_cursor() as cur:
        cur.executemany(sql, rows)
    return len(rows)


# ─── Structured Query Methods ───
# All return list[dict] matching the RAGEngine evidence format:
#   {"text": str, "source": str, "category": str, "timestamp": str, "relevance_score": float}


def get_medications(patient_id: str = PATIENT_ID) -> list[dict]:
    with get_cursor() as cur:
        cur.execute(
            "SELECT name, dose, route, frequency, indication, status, start_date, notes "
            "FROM AmbientDx.Medications WHERE patient_id = ?",
            [patient_id],
        )
        results = []
        for r in cur.fetchall():
            name, dose, route, freq, indication, status, start, notes = r
            text = (
                f"MEDICATION: {name} {dose} {route} {freq}. "
                f"Indication: {indication}. Status: {status}."
            )
            if notes:
                text += f" Notes: {notes}"
            results.append({
                "text": text,
                "source": f"Medication List — {name}",
                "category": "medications",
                "timestamp": start,
                "relevance_score": 1.0,
            })
        return results


def get_allergies(patient_id: str = PATIENT_ID) -> list[dict]:
    with get_cursor() as cur:
        cur.execute(
            "SELECT allergen, reaction, severity, documented_date, source_info "
            "FROM AmbientDx.Allergies WHERE patient_id = ?",
            [patient_id],
        )
        results = []
        for r in cur.fetchall():
            allergen, reaction, severity, doc_date, source = r
            text = f"ALLERGY: {allergen} — Reaction: {reaction}. Severity: {severity}."
            if doc_date:
                text += f" Documented: {doc_date}."
            if source:
                text += f" Source: {source}."
            results.append({
                "text": text,
                "source": "Allergy List",
                "category": "allergies",
                "timestamp": doc_date or "",
                "relevance_score": 1.0,
            })
        return results


def get_problems(patient_id: str = PATIENT_ID) -> list[dict]:
    with get_cursor() as cur:
        cur.execute(
            "SELECT problem, status, icd10, critical_flag "
            "FROM AmbientDx.Problems WHERE patient_id = ?",
            [patient_id],
        )
        lines = []
        for r in cur.fetchall():
            prob, stat, icd, crit = r
            line = f"- {prob} — Status: {stat}"
            if crit:
                line += " *** CRITICAL FLAG ***"
            lines.append(line)
        if not lines:
            return []
        return [{
            "text": "PROBLEM LIST:\n" + "\n".join(lines),
            "source": "Problem List",
            "category": "problems",
            "timestamp": "",
            "relevance_score": 1.0,
        }]


def get_critical_problems(patient_id: str = PATIENT_ID) -> list[dict]:
    with get_cursor() as cur:
        cur.execute(
            "SELECT problem, status, icd10 "
            "FROM AmbientDx.Problems WHERE patient_id = ? AND critical_flag = 1",
            [patient_id],
        )
        results = []
        for r in cur.fetchall():
            prob, stat, icd = r
            results.append({
                "text": f"CRITICAL PROBLEM: {prob} — Status: {stat}",
                "source": "Problem List — Critical",
                "category": "problems",
                "timestamp": "",
                "relevance_score": 1.0,
            })
        return results


def get_lab_trend(patient_id: str, lab_name: str) -> list[dict]:
    with get_cursor() as cur:
        cur.execute(
            "SELECT timepoint, timestamp_val, lab_value, unit, ref_range, flag, note "
            "FROM AmbientDx.Labs WHERE patient_id = ? AND lab_name = ? "
            "ORDER BY timestamp_val",
            [patient_id, lab_name],
        )
        rows = cur.fetchall()
        if not rows:
            return []
        lines = [f"{lab_name.upper()} TREND:"]
        for r in rows:
            tp, ts, val, unit, ref, flag, note = r
            line = f"  {tp}: {val} {unit} (ref {ref}) [{flag}]"
            if note:
                line += f" — {note}"
            lines.append(line)
        return [{
            "text": "\n".join(lines),
            "source": f"Lab Trend — {lab_name.title()}",
            "category": "labs",
            "timestamp": rows[-1][1],
            "relevance_score": 1.0,
        }]


def get_recent_labs(patient_id: str, timepoint: str | None = None) -> list[dict]:
    """Get all lab results at the most recent (or given) timepoint."""
    with get_cursor() as cur:
        if timepoint:
            cur.execute(
                "SELECT timepoint, timestamp_val, lab_name, lab_value, unit, ref_range, flag, note "
                "FROM AmbientDx.Labs WHERE patient_id = ? AND timepoint = ?",
                [patient_id, timepoint],
            )
        else:
            cur.execute(
                "SELECT TOP 1 timepoint FROM AmbientDx.Labs "
                "WHERE patient_id = ? ORDER BY timestamp_val DESC",
                [patient_id],
            )
            row = cur.fetchone()
            if not row:
                return []
            latest_tp = row[0]
            cur.execute(
                "SELECT timepoint, timestamp_val, lab_name, lab_value, unit, ref_range, flag, note "
                "FROM AmbientDx.Labs WHERE patient_id = ? AND timepoint = ?",
                [patient_id, latest_tp],
            )
        rows = cur.fetchall()
        if not rows:
            return []
        tp_label = rows[0][0]
        ts = rows[0][1]
        lines = [f"LAB RESULTS — {tp_label} ({ts}):"]
        for r in rows:
            _, _, name, val, unit, ref, flag, note = r
            line = f"  {name}: {val} {unit} (ref {ref}) [{flag}]"
            if note:
                line += f" — {note}"
            lines.append(line)
        return [{
            "text": "\n".join(lines),
            "source": f"Labs — {tp_label}",
            "category": "labs",
            "timestamp": ts,
            "relevance_score": 1.0,
        }]


def get_vitals_trend(patient_id: str = PATIENT_ID) -> list[dict]:
    with get_cursor() as cur:
        cur.execute(
            "SELECT timepoint, timestamp_val, bp_systolic, bp_diastolic, "
            "heart_rate, resp_rate, spo2, temp "
            "FROM AmbientDx.Vitals WHERE patient_id = ? ORDER BY timestamp_val",
            [patient_id],
        )
        rows = cur.fetchall()
        if not rows:
            return []
        lines = ["VITALS TREND — POD#6 (Today):"]
        for r in rows:
            tp, ts, sys, dia, hr, rr, spo2, temp = r
            lines.append(
                f"  {tp}: BP {sys}/{dia}, HR {hr}, RR {rr}, SpO2 {spo2}%, T {temp}°C"
            )
        first = rows[0]
        last = rows[-1]
        lines.append(
            f"TREND: Progressive hypotension ({first[2]}/{first[3]} → {last[2]}/{last[3]}) "
            f"with tachycardia ({first[4]} → {last[4]})."
        )
        return [{
            "text": "\n".join(lines),
            "source": "Vitals — POD#6 trend",
            "category": "vitals",
            "timestamp": rows[-1][1],
            "relevance_score": 1.0,
        }]


def get_heparin_status(patient_id: str = PATIENT_ID) -> list[dict]:
    """Specific safety check: is patient on heparin?"""
    with get_cursor() as cur:
        cur.execute(
            "SELECT name, dose, route, frequency, status, notes "
            "FROM AmbientDx.Medications "
            "WHERE patient_id = ? AND LOWER(name) LIKE '%heparin%' AND status LIKE '%Active%'",
            [patient_id],
        )
        rows = cur.fetchall()
        results = []
        for r in rows:
            name, dose, route, freq, status, notes = r
            results.append({
                "text": f"ACTIVE HEPARIN: {name} {dose} {route} {freq}. Status: {status}. {notes or ''}",
                "source": f"Medication List — {name}",
                "category": "medications",
                "timestamp": "",
                "relevance_score": 1.0,
            })
        return results
