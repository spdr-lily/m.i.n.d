from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python import PythonOperator, BranchPythonOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.operators.dummy import DummyOperator

from config import DEFAULT_ARGS, DB_CONN_ID


def check_suicidal_ideation(**context) -> list:
    hook = PostgresHook(postgres_conn_id=DB_CONN_ID)
    conn = hook.get_conn()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT c.consultation_uuid, c.profile_uuid, sr.response_value,
               c.consultation_date
        FROM clinical.scale_response sr
        JOIN clinical.scale_question sq ON sr.question_id = sq.question_id
        JOIN clinical.assessment_scale a ON sq.scale_id = a.scale_id
        JOIN clinical.clinical_consultation c ON sr.consultation_uuid = c.consultation_uuid
        WHERE sq.question_order = 9
          AND a.scale_name = 'PHQ-9'
          AND sr.response_value > 0
          AND c.consultation_date >= now() - interval '24 hours'
    """)
    rows = cursor.fetchall()
    cursor.close()
    conn.close()

    alerts = []
    for row in rows:
        severity = "critical" if row[2] >= 2 else "high"
        alerts.append({
            "type": "suicidal_ideation",
            "severity": severity,
            "consultation_uuid": row[0],
            "patient_uuid": row[1],
            "score": row[2],
            "date": row[3].isoformat(),
        })
    return alerts


def check_high_confidence_deterioration(**context) -> list:
    hook = PostgresHook(postgres_conn_id=DB_CONN_ID)
    conn = hook.get_conn()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT di.consultation_uuid, c.profile_uuid,
               d.disorder_name, di.inference_probability,
               di.created_at
        FROM clinical.diagnostic_inference di
        JOIN clinical.clinical_consultation c ON di.consultation_uuid = c.consultation_uuid
        JOIN diagnostic.disorder d ON di.disorder_id = d.disorder_id
        WHERE di.inference_probability >= 0.8
          AND di.created_at >= now() - interval '24 hours'
        ORDER BY di.inference_probability DESC
    """)
    rows = cursor.fetchall()
    cursor.close()
    conn.close()

    return [
        {
            "type": "high_confidence",
            "severity": "high",
            "consultation_uuid": row[0],
            "patient_uuid": row[1],
            "disorder": row[2],
            "probability": float(row[3]),
            "date": row[4].isoformat(),
        }
        for row in rows
    ]


def run_all_alerts(**context) -> dict:
    suicidal = check_suicidal_ideation(**context)
    high_conf = check_high_confidence_deterioration(**context)
    all_alerts = suicidal + high_conf
    return {
        "total_alerts": len(all_alerts),
        "suicidal_ideation": len(suicidal),
        "high_confidence": len(high_conf),
        "alerts": all_alerts,
    }


with DAG(
    dag_id="alert_generation",
    default_args=DEFAULT_ARGS,
    description="Clinical alert generation and monitoring",
    schedule="0 */6 * * *",
    start_date=datetime(2026, 1, 1),
    catchup=False,
    tags=["alerts", "clinical", "safety"],
) as dag:

    generate_alerts = PythonOperator(
        task_id="generate_alerts",
        python_callable=run_all_alerts,
    )
