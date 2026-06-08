import csv
import json
import os
from datetime import date
from app.core.database import engine
from sqlalchemy import text


QUERY = """
WITH consultation_base AS (
    SELECT
        c.consultation_key,
        c.consultation_uuid::text,
        c.date_key,
        d.full_date AS consultation_date,
        c.patient_key,
        p.patient_uuid::text,
        p.age_group,
        p.sex,
        p.education_level,
        c.symptom_count,
        c.total_intensity::float AS total_intensity,
        c.avg_intensity::float AS avg_intensity,
        c.scale_count,
        c.has_inference,
        c.inference_count
    FROM dw.fact_consultation c
    JOIN dw.dim_date d ON d.date_key = c.date_key
    JOIN dw.dim_patient p ON p.patient_key = c.patient_key
),
medications AS (
    SELECT
        cs.consultation_uuid::text,
        STRING_AGG(DISTINCT m.name, '; ' ORDER BY m.name) AS medication_names,
        STRING_AGG(DISTINCT m.classification, '; ' ORDER BY m.classification) AS medication_classifications,
        COUNT(DISTINCT m.medication_id) AS medication_count
    FROM clinical.prescriptions p
    JOIN clinical.prescription_items pi ON pi.prescription_uuid = p.prescription_uuid
    JOIN clinical.medications m ON m.medication_id = pi.medication_id
    JOIN clinical.clinical_consultation cs ON cs.consultation_uuid = p.consultation_uuid
    GROUP BY cs.consultation_uuid
),
scale_pivot AS (
    SELECT
        sr.consultation_key,
        MAX(CASE WHEN sc.scale_name = 'PHQ-9' THEN sr.total_score END) AS phq9_score,
        MAX(CASE WHEN sc.scale_name = 'GAD-7' THEN sr.total_score END) AS gad7_score,
        MAX(CASE WHEN sc.scale_name = 'PHQ-9' THEN sr.severity_level END) AS phq9_severity,
        MAX(CASE WHEN sc.scale_name = 'GAD-7' THEN sr.severity_level END) AS gad7_severity
    FROM dw.fact_scale_response sr
    JOIN dw.dim_scale sc ON sc.scale_key = sr.scale_key
    GROUP BY sr.consultation_key
),
symptom_agg AS (
    SELECT
        s.consultation_key,
        STRING_AGG(s.symptom_name, '; ' ORDER BY s.intensity DESC) AS symptom_names,
        MAX(s.intensity) AS max_symptom_intensity,
        COUNT(*) FILTER (WHERE s.is_present) AS present_symptom_count
    FROM dw.fact_symptom s
    GROUP BY s.consultation_key
),
primary_diagnosis AS (
    SELECT
        d.consultation_key,
        di.disorder_name AS primary_diagnosis,
        d.probability::float AS diagnosis_probability,
        d.confidence_level::float AS diagnosis_confidence,
        d.disorder_key
    FROM (
        SELECT *,
            ROW_NUMBER() OVER (PARTITION BY consultation_key ORDER BY probability DESC) AS rn
        FROM dw.fact_diagnosis
    ) d
    JOIN dw.dim_disorder di ON di.disorder_key = d.disorder_key
    WHERE d.rn = 1
),
all_diagnoses AS (
    SELECT
        d.consultation_key,
        STRING_AGG(di.disorder_name || ' (' || ROUND(d.probability::numeric, 3)::text || ')', '; ' ORDER BY d.probability DESC) AS all_diagnoses
    FROM dw.fact_diagnosis d
    JOIN dw.dim_disorder di ON di.disorder_key = d.disorder_key
    GROUP BY d.consultation_key
)
SELECT
    cb.*,
    sp.phq9_score::float,
    sp.gad7_score::float,
    sp.phq9_severity,
    sp.gad7_severity,
    sa.symptom_names,
    sa.max_symptom_intensity::float,
    sa.present_symptom_count,
    pd.primary_diagnosis,
    pd.diagnosis_probability,
    pd.diagnosis_confidence,
    ad.all_diagnoses,
    md.medication_names,
    md.medication_classifications,
    md.medication_count
FROM consultation_base cb
LEFT JOIN scale_pivot sp ON sp.consultation_key = cb.consultation_key
LEFT JOIN symptom_agg sa ON sa.consultation_key = cb.consultation_key
LEFT JOIN primary_diagnosis pd ON pd.consultation_key = cb.consultation_key
LEFT JOIN all_diagnoses ad ON ad.consultation_key = cb.consultation_key
LEFT JOIN medications md ON md.consultation_uuid = cb.consultation_uuid
ORDER BY cb.patient_uuid, cb.consultation_date
"""


def build_clinical_dataset():
    with engine.connect() as conn:
        rows = conn.execute(text(QUERY)).mappings().all()

    # Build evolution metrics per patient
    prev = {}
    enriched = []
    for r in rows:
        r = dict(r)
        puid = r["patient_uuid"]
        p = prev.get(puid)

        if p:
            r["prev_consultation_date"] = p["consultation_date"].isoformat()
            r["days_since_last_consult"] = (r["consultation_date"] - p["consultation_date"]).days
            r["phq9_delta"] = round((r["phq9_score"] or 0) - (p["phq9_score"] or 0), 2)
            r["gad7_delta"] = round((r["gad7_score"] or 0) - (p["gad7_score"] or 0), 2)
            r["diagnosis_changed"] = (r["primary_diagnosis"] != p["primary_diagnosis"])
            r["consult_num"] = p.get("consult_num", 0) + 1
        else:
            r["prev_consultation_date"] = None
            r["days_since_last_consult"] = None
            r["phq9_delta"] = None
            r["gad7_delta"] = None
            r["diagnosis_changed"] = None
            r["consult_num"] = 1

        prev[puid] = r
        enriched.append(r)

    # Output CSV
    fieldnames = [
        "patient_uuid", "age_group", "sex", "education_level",
        "consultation_uuid", "consultation_date", "consult_num",
        "symptom_count", "present_symptom_count", "avg_intensity", "total_intensity",
        "max_symptom_intensity", "symptom_names",
        "phq9_score", "phq9_severity", "gad7_score", "gad7_severity",
        "primary_diagnosis", "diagnosis_probability", "diagnosis_confidence", "all_diagnoses",
        "medication_names", "medication_classifications", "medication_count",
        "has_inference", "inference_count",
        "prev_consultation_date", "days_since_last_consult",
        "phq9_delta", "gad7_delta", "diagnosis_changed",
    ]

    os.makedirs("data/datasets", exist_ok=True)
    outpath = "data/datasets/clinical_dataset.csv"

    with open(outpath, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        w.writeheader()
        w.writerows(enriched)

    print(f"[OK] Clinical dataset written: {outpath}")
    print(f"     Rows: {len(enriched)}")
    print(f"     Columns: {len(fieldnames)}")
    print(f"     Patients: {len(set(r['patient_uuid'] for r in enriched))}")
    print(f"     Date range: {enriched[0]['consultation_date']} to {enriched[-1]['consultation_date']}")


if __name__ == "__main__":
    build_clinical_dataset()
