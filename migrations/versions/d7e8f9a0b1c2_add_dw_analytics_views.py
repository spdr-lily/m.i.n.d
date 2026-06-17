"""add DW analytics views (prevalence, comorbidity, score distribution, patient summary, professional workload)

Revision ID: d7e8f9a0b1c2
Revises: c608eee4970f
Create Date: 2026-06-16 18:00:00.000000
"""
from typing import Sequence, Union
from alembic import op

revision: str = "d7e8f9a0b1c2"
down_revision: Union[str, None] = "c608eee4970f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


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
}


def upgrade() -> None:
    for view_name, ddl in VIEWS.items():
        op.execute(ddl)
        print(f"  Created/replaced view: dw.{view_name}")


def downgrade() -> None:
    for view_name in VIEWS:
        op.execute(f"DROP VIEW IF EXISTS dw.{view_name} CASCADE")
