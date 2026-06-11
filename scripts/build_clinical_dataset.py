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
        MAX(CASE WHEN sc.scale_name = 'MADRS' THEN sr.total_score END) AS madrs_score,
        MAX(CASE WHEN sc.scale_name = 'MDQ' THEN sr.total_score END) AS mdq_score,
        MAX(CASE WHEN sc.scale_name = 'PCL-5' THEN sr.total_score END) AS pcl5_score,
        MAX(CASE WHEN sc.scale_name = 'Y-BOCS' THEN sr.total_score END) AS ybocs_score,
        MAX(CASE WHEN sc.scale_name = 'AUDIT' THEN sr.total_score END) AS audit_score,
        MAX(CASE WHEN sc.scale_name = 'ASRM' THEN sr.total_score END) AS asrm_score,
        MAX(CASE WHEN sc.scale_name = 'ASRS' THEN sr.total_score END) AS asrs_score,
        MAX(CASE WHEN sc.scale_name = 'AQ-10' THEN sr.total_score END) AS aq10_score,
        MAX(CASE WHEN sc.scale_name = 'PHQ-9' THEN sr.severity_level END) AS phq9_severity,
        MAX(CASE WHEN sc.scale_name = 'GAD-7' THEN sr.severity_level END) AS gad7_severity,
        MAX(CASE WHEN sc.scale_name = 'MADRS' THEN sr.severity_level END) AS madrs_severity,
        MAX(CASE WHEN sc.scale_name = 'MDQ' THEN sr.severity_level END) AS mdq_severity,
        MAX(CASE WHEN sc.scale_name = 'PCL-5' THEN sr.severity_level END) AS pcl5_severity,
        MAX(CASE WHEN sc.scale_name = 'Y-BOCS' THEN sr.severity_level END) AS ybocs_severity,
        MAX(CASE WHEN sc.scale_name = 'AUDIT' THEN sr.severity_level END) AS audit_severity,
        MAX(CASE WHEN sc.scale_name = 'ASRM' THEN sr.severity_level END) AS asrm_severity,
        MAX(CASE WHEN sc.scale_name = 'ASRS' THEN sr.severity_level END) AS asrs_severity,
        MAX(CASE WHEN sc.scale_name = 'AQ-10' THEN sr.severity_level END) AS aq10_severity
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
    sp.madrs_score::float,
    sp.mdq_score::float,
    sp.pcl5_score::float,
    sp.ybocs_score::float,
    sp.audit_score::float,
    sp.asrm_score::float,
    sp.asrs_score::float,
    sp.aq10_score::float,
    sp.phq9_severity,
    sp.gad7_severity,
    sp.madrs_severity,
    sp.mdq_severity,
    sp.pcl5_severity,
    sp.ybocs_severity,
    sp.audit_severity,
    sp.asrm_severity,
    sp.asrs_severity,
    sp.aq10_severity,
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
    scale_cols = ["phq9", "gad7", "madrs", "mdq", "pcl5", "ybocs", "audit", "asrm", "asrs", "aq10"]

    prev = {}
    enriched = []
    for r in rows:
        r = dict(r)
        puid = r["patient_uuid"]
        p = prev.get(puid)

        if p:
            r["prev_consultation_date"] = p["consultation_date"].isoformat()
            r["days_since_last_consult"] = (r["consultation_date"] - p["consultation_date"]).days
            for sc in scale_cols:
                r[f"{sc}_delta"] = round((r[f"{sc}_score"] or 0) - (p[f"{sc}_score"] or 0), 2)
            r["diagnosis_changed"] = (r["primary_diagnosis"] != p["primary_diagnosis"])
            r["consult_num"] = p.get("consult_num", 0) + 1
        else:
            r["prev_consultation_date"] = None
            r["days_since_last_consult"] = None
            for sc in scale_cols:
                r[f"{sc}_delta"] = None
            r["diagnosis_changed"] = None
            r["consult_num"] = 1

        prev[puid] = r
        enriched.append(r)

    # Output CSV
    scale_score_fields = [f"{sc}_score" for sc in scale_cols]
    scale_severity_fields = [f"{sc}_severity" for sc in scale_cols]
    scale_delta_fields = [f"{sc}_delta" for sc in scale_cols]
    fieldnames = [
        "patient_uuid", "age_group", "sex", "education_level",
        "consultation_uuid", "consultation_date", "consult_num",
        "symptom_count", "present_symptom_count", "avg_intensity", "total_intensity",
        "max_symptom_intensity", "symptom_names",
        *scale_score_fields, *scale_severity_fields,
        "primary_diagnosis", "diagnosis_probability", "diagnosis_confidence", "all_diagnoses",
        "medication_names", "medication_classifications", "medication_count",
        "has_inference", "inference_count",
        "prev_consultation_date", "days_since_last_consult",
        *scale_delta_fields, "diagnosis_changed",
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
