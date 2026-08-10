"""DW analytics views.

Central definition of all DW materialized/regular analytics views. Keep in sync
with the historical DDL embedded in the alembic migrations:

- ``migrations/versions/d7e8f9a0b1c2_add_dw_analytics_views.py``
- ``migrations/versions/a2b3c4d5e6f7_add_advanced_dw_analytics_views.py``

Those migrations only create the views when the ``dw`` schema already exists
(fresh installs run the ETL, which is the single source of truth here).
"""

from sqlalchemy import text
from sqlalchemy.orm import Session

VIEWS = {
    "vw_prevalence_trends": """
        CREATE OR REPLACE VIEW dw.vw_prevalence_trends AS
        SELECT
            dd.disorder_name,
            dd.disorder_category,
            d.year,
            d.month,
            d.year || '-' || LPAD(d.month::text, 2, '0') AS year_month,
            COUNT(*) AS diagnosis_count,
            ROUND(AVG(fd.probability::numeric)::numeric, 4) AS avg_probability,
            ROUND(MAX(fd.probability::numeric)::numeric, 4) AS max_probability,
            COUNT(DISTINCT fd.patient_key) AS unique_patients
        FROM dw.fact_diagnosis fd
        JOIN dw.dim_disorder dd ON fd.disorder_key = dd.disorder_key
        JOIN dw.dim_date d ON fd.date_key = d.date_key
        GROUP BY dd.disorder_name, dd.disorder_category, d.year, d.month
    """,
    "vw_comorbidity_pairs": """
        CREATE OR REPLACE VIEW dw.vw_comorbidity_pairs AS
        WITH consult_disorders AS (
            SELECT fd.consultation_key, dd.disorder_name, dd.disorder_category
            FROM dw.fact_diagnosis fd
            JOIN dw.dim_disorder dd ON fd.disorder_key = dd.disorder_key
            GROUP BY fd.consultation_key, dd.disorder_name, dd.disorder_category
        )
        SELECT
            a.disorder_name AS disorder_a,
            a.disorder_category AS category_a,
            b.disorder_name AS disorder_b,
            b.disorder_category AS category_b,
            COUNT(*) AS co_occurrence_count,
            ROUND(COUNT(*)::numeric / (
                SELECT COUNT(DISTINCT consultation_key) FROM dw.fact_diagnosis
            ) * 100, 2) AS prevalence_pct
        FROM consult_disorders a
        JOIN consult_disorders b ON a.consultation_key = b.consultation_key
            AND a.disorder_name < b.disorder_name
        GROUP BY a.disorder_name, a.disorder_category, b.disorder_name, b.disorder_category
    """,
    "vw_score_distribution": """
        CREATE OR REPLACE VIEW dw.vw_score_distribution AS
        SELECT
            ds.scale_name,
            'Clinical'::varchar(100) AS scale_category,
            COUNT(*) AS total_responses,
            ROUND(AVG(fsr.total_score::numeric)::numeric, 2) AS mean_score,
            ROUND(STDDEV(fsr.total_score::numeric)::numeric, 2) AS stddev_score,
            ROUND(MIN(fsr.total_score::numeric)::numeric, 2) AS min_score,
            ROUND(MAX(fsr.total_score::numeric)::numeric, 2) AS max_score,
            ROUND(PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY fsr.total_score)::numeric, 2) AS median_score,
            ROUND(AVG(fsr.percentage_score::numeric)::numeric, 2) AS mean_pct,
            COUNT(DISTINCT fsr.patient_key) AS unique_patients
        FROM dw.fact_scale_response fsr
        JOIN dw.dim_scale ds ON fsr.scale_key = ds.scale_key
        GROUP BY ds.scale_name, ds.scale_description, ds.max_score
    """,
    "vw_scale_severity_distribution": """
        CREATE OR REPLACE VIEW dw.vw_scale_severity_distribution AS
        SELECT
            ds.scale_name,
            fsr.severity_level,
            COUNT(*) AS response_count,
            ROUND(AVG(fsr.total_score::numeric)::numeric, 2) AS avg_score
        FROM dw.fact_scale_response fsr
        JOIN dw.dim_scale ds ON fsr.scale_key = ds.scale_key
        GROUP BY ds.scale_name, fsr.severity_level
        ORDER BY ds.scale_name, fsr.severity_level
    """,
    "vw_patient_summary": """
        CREATE OR REPLACE VIEW dw.vw_patient_summary AS
        SELECT
            dp.patient_key,
            dp.patient_uuid,
            dp.age_group,
            dp.sex,
            dp.education_level,
            dp.ethnicity,
            COUNT(DISTINCT fc.consultation_key) AS total_consultations,
            COUNT(DISTINCT fd.diagnosis_key) AS total_diagnoses,
            COUNT(DISTINCT dd.disorder_key) AS unique_disorders,
            ROUND(AVG(fc.avg_intensity::numeric)::numeric, 2) AS avg_symptom_intensity,
            MAX(fc.max_probability::numeric) AS max_diagnosis_probability,
            COUNT(DISTINCT fsr.scale_key) AS unique_scales_taken,
            ROUND(AVG(fsr.percentage_score::numeric)::numeric, 2) AS avg_scale_pct
        FROM dw.dim_patient dp
        LEFT JOIN dw.fact_consultation fc ON dp.patient_key = fc.patient_key
        LEFT JOIN dw.fact_diagnosis fd ON fc.consultation_key = fd.consultation_key
        LEFT JOIN dw.dim_disorder dd ON fd.disorder_key = dd.disorder_key
        LEFT JOIN dw.fact_scale_response fsr ON fc.consultation_key = fsr.consultation_key
        GROUP BY dp.patient_key, dp.patient_uuid, dp.age_group, dp.sex,
                 dp.education_level, dp.ethnicity
    """,
    "vw_professional_workload": """
        CREATE OR REPLACE VIEW dw.vw_professional_workload AS
        SELECT
            dpro.full_name,
            dpro.profession,
            dpro.specialty,
            COUNT(DISTINCT fc.consultation_key) AS total_consultations,
            COUNT(DISTINCT fc.patient_key) AS unique_patients,
            COUNT(DISTINCT fd.diagnosis_key) AS total_diagnoses,
            ROUND(AVG(fc.symptom_count::numeric)::numeric, 1) AS avg_symptoms_per_consult,
            ROUND(AVG(fc.avg_intensity::numeric)::numeric, 2) AS avg_symptom_intensity,
            ROUND(AVG(fc.max_probability::numeric)::numeric, 4) AS avg_max_probability,
            COUNT(DISTINCT fsr.scale_key) AS scales_used
        FROM dw.dim_professional dpro
        LEFT JOIN dw.fact_consultation fc ON dpro.professional_key = fc.professional_key
        LEFT JOIN dw.fact_diagnosis fd ON fc.consultation_key = fd.consultation_key
        LEFT JOIN dw.fact_scale_response fsr ON fc.consultation_key = fsr.consultation_key
        GROUP BY dpro.full_name, dpro.profession, dpro.specialty
    """,
    "vw_demographic_summary": """
        CREATE OR REPLACE VIEW dw.vw_demographic_summary AS
        SELECT
            dp.age_group,
            dp.sex,
            dp.education_level,
            dp.ethnicity,
            COUNT(*) AS patient_count,
            ROUND(AVG(fc_total.consult_count::numeric)::numeric, 1) AS avg_consultations
        FROM dw.dim_patient dp
        LEFT JOIN (
            SELECT patient_key, COUNT(*) AS consult_count
            FROM dw.fact_consultation
            GROUP BY patient_key
        ) fc_total ON dp.patient_key = fc_total.patient_key
        GROUP BY dp.age_group, dp.sex, dp.education_level, dp.ethnicity
    """,
    "vw_monthly_consultation_stats": """
        CREATE OR REPLACE VIEW dw.vw_monthly_consultation_stats AS
        SELECT
            d.year,
            d.month,
            d.year || '-' || LPAD(d.month::text, 2, '0') AS year_month,
            COUNT(*) AS total_consultations,
            COUNT(DISTINCT fc.patient_key) AS unique_patients,
            ROUND(AVG(fc.symptom_count::numeric)::numeric, 1) AS avg_symptoms,
            ROUND(AVG(fc.total_intensity::numeric)::numeric, 2) AS avg_total_intensity,
            SUM(CASE WHEN fc.has_inference THEN 1 ELSE 0 END) AS consultations_with_inference,
            ROUND(AVG(fc.max_probability::numeric)::numeric, 4) AS avg_max_probability
        FROM dw.fact_consultation fc
        JOIN dw.dim_date d ON fc.date_key = d.date_key
        GROUP BY d.year, d.month
    """,
    "vw_symptom_prevalence_by_disorder": """
        CREATE OR REPLACE VIEW dw.vw_symptom_prevalence_by_disorder AS
        SELECT
            dd.disorder_name,
            dd.disorder_category,
            fs.symptom_name,
            COUNT(DISTINCT fs.consultation_key) AS consultation_count,
            ROUND(AVG(fs.intensity::numeric)::numeric, 2) AS avg_intensity,
            COUNT(*) AS total_observations,
            ROUND(COUNT(DISTINCT fs.consultation_key)::numeric / NULLIF(
                (SELECT COUNT(DISTINCT f.consultation_key) FROM dw.fact_diagnosis f
                 JOIN dw.dim_disorder d ON f.disorder_key = d.disorder_key
                 WHERE d.disorder_name = dd.disorder_name), 0
            ) * 100, 1) AS prevalence_pct
        FROM dw.fact_symptom fs
        JOIN dw.dim_disorder dd ON fs.disorder_key = dd.disorder_key
        GROUP BY dd.disorder_name, dd.disorder_category, fs.symptom_name
        HAVING COUNT(DISTINCT fs.consultation_key) >= 2
    """,
    "vw_scale_trends_monthly": """
        CREATE OR REPLACE VIEW dw.vw_scale_trends_monthly AS
        SELECT
            ds.scale_name,
            d.year,
            d.month,
            d.year || '-' || LPAD(d.month::text, 2, '0') AS year_month,
            COUNT(*) AS response_count,
            ROUND(AVG(fsr.total_score::numeric)::numeric, 2) AS avg_score,
            ROUND(AVG(fsr.percentage_score::numeric)::numeric, 2) AS avg_pct,
            ROUND(STDDEV(fsr.total_score::numeric)::numeric, 2) AS stddev_score,
            ROUND(MIN(fsr.total_score::numeric)::numeric, 2) AS min_score,
            ROUND(MAX(fsr.total_score::numeric)::numeric, 2) AS max_score,
            COUNT(DISTINCT fsr.patient_key) AS unique_patients
        FROM dw.fact_scale_response fsr
        JOIN dw.dim_scale ds ON fsr.scale_key = ds.scale_key
        JOIN dw.dim_date d ON fsr.date_key = d.date_key
        GROUP BY ds.scale_name, d.year, d.month
    """,
    "vw_disorder_by_demographic": """
        CREATE OR REPLACE VIEW dw.vw_disorder_by_demographic AS
        SELECT
            dd.disorder_name,
            dd.disorder_category,
            dp.age_group,
            dp.sex,
            COUNT(DISTINCT fd.patient_key) AS patient_count,
            COUNT(*) AS diagnosis_count,
            ROUND(AVG(fd.probability::numeric)::numeric, 4) AS avg_probability,
            ROUND(COUNT(DISTINCT fd.patient_key)::numeric / NULLIF(
                (SELECT COUNT(*) FROM dw.dim_patient WHERE age_group = dp.age_group AND sex = dp.sex), 0
            ) * 100, 1) AS penetration_pct
        FROM dw.fact_diagnosis fd
        JOIN dw.dim_disorder dd ON fd.disorder_key = dd.disorder_key
        JOIN dw.dim_patient dp ON fd.patient_key = dp.patient_key
        GROUP BY dd.disorder_name, dd.disorder_category, dp.age_group, dp.sex
    """,
}


def create_dw_views(session: Session) -> None:
    """Create (or replace) all DW analytics views."""
    for view_name, ddl in VIEWS.items():
        session.execute(text(ddl))
    session.commit()
