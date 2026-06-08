from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook

from config import DEFAULT_ARGS, DB_CONN_ID


QUALITY_CHECKS = {
    "missing_patient_profiles": """
        SELECT count(*) FROM core.patient_identity i
        LEFT JOIN core.patient_profile p ON i.patient_uuid = p.patient_uuid
        WHERE p.profile_uuid IS NULL
    """,
    "consultations_without_episode": """
        SELECT count(*) FROM clinical.clinical_consultation c
        LEFT JOIN clinical.clinical_episode e ON c.episode_uuid = e.episode_uuid
        WHERE e.episode_uuid IS NULL
    """,
    "scale_responses_without_consultation": """
        SELECT count(*) FROM clinical.scale_response sr
        LEFT JOIN clinical.clinical_consultation c ON sr.consultation_uuid = c.consultation_uuid
        WHERE c.consultation_uuid IS NULL
    """,
    "orphan_inferences": """
        SELECT count(*) FROM clinical.diagnostic_inference di
        LEFT JOIN clinical.clinical_consultation c ON di.consultation_uuid = c.consultation_uuid
        WHERE c.consultation_uuid IS NULL
    """,
    "negative_probabilities": """
        SELECT count(*) FROM clinical.diagnostic_inference
        WHERE inference_probability < 0 OR inference_probability > 1
    """,
    "future_dates": """
        SELECT count(*) FROM clinical.clinical_consultation
        WHERE created_at > now()
    """,
}


def run_quality_checks(**context) -> dict:
    hook = PostgresHook(postgres_conn_id=DB_CONN_ID)
    conn = hook.get_conn()
    cursor = conn.cursor()
    results = {}
    all_pass = True
    for check_name, query in QUALITY_CHECKS.items():
        cursor.execute(query)
        count = cursor.fetchone()[0]
        results[check_name] = count
        if count > 0:
            all_pass = False
    cursor.close()
    conn.close()
    return {"all_checks_passed": all_pass, "anomalies": results}


with DAG(
    dag_id="data_quality_checks",
    default_args=DEFAULT_ARGS,
    description="Daily data integrity and quality checks",
    schedule="0 3 * * *",
    start_date=datetime(2026, 1, 1),
    catchup=False,
    tags=["quality", "monitoring"],
) as dag:

    run_checks = PythonOperator(
        task_id="run_quality_checks",
        python_callable=run_quality_checks,
    )
