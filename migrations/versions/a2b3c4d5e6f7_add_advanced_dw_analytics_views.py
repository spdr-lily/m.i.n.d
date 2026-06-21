"""add advanced DW analytics views (symptom prevalence, scale trends, disorder by demographic)

Revision ID: a2b3c4d5e6f7
Revises: 031c8a8ec7b8
Create Date: 2026-06-18 12:00:00.000000
"""
from typing import Sequence, Union
from alembic import op

revision: str = "a2b3c4d5e6f7"
down_revision: Union[str, None] = "031c8a8ec7b8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

VIEWS = {
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


def upgrade() -> None:
    for view_name, ddl in VIEWS.items():
        op.execute(ddl)
        print(f"  Created/replaced view: dw.{view_name}")


def downgrade() -> None:
    for view_name in VIEWS:
        op.execute(f"DROP VIEW IF EXISTS dw.{view_name} CASCADE")
