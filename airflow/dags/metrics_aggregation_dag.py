from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook

from config import DEFAULT_ARGS, DB_CONN_ID


def aggregate_daily_metrics(**context) -> dict:
    hook = PostgresHook(postgres_conn_id=DB_CONN_ID)
    conn = hook.get_conn()
    cursor = conn.cursor()

    metrics = {}

    cursor.execute("SELECT count(*) FROM core.patient_identity")
    metrics["total_patients"] = cursor.fetchone()[0]

    cursor.execute("SELECT count(*) FROM clinical.clinical_consultation WHERE created_at >= now() - interval '24 hours'")
    metrics["consultations_last_24h"] = cursor.fetchone()[0]

    cursor.execute("SELECT count(*) FROM clinical.diagnostic_inference WHERE created_at >= now() - interval '24 hours'")
    metrics["inferences_last_24h"] = cursor.fetchone()[0]

    cursor.execute("""
        SELECT d.disorder_name, count(*) as cnt
        FROM clinical.diagnostic_inference di
        JOIN diagnostic.disorder d ON di.disorder_id = d.disorder_id
        WHERE di.created_at >= now() - interval '7 days'
        GROUP BY d.disorder_name ORDER BY cnt DESC LIMIT 5
    """)
    metrics["top_disorders_7d"] = [
        {"disorder": row[0], "count": row[1]} for row in cursor.fetchall()
    ]

    cursor.execute("""
        SELECT a.scale_name, round(avg(sr.response_value), 2) as avg_score
        FROM clinical.scale_response sr
        JOIN clinical.scale_question sq ON sr.question_id = sq.question_id
        JOIN clinical.assessment_scale a ON sq.scale_id = a.scale_id
        WHERE sr.created_at >= now() - interval '7 days'
        GROUP BY a.scale_name
    """)
    metrics["avg_scale_scores_7d"] = {
        row[0]: row[1] for row in cursor.fetchall()
    }

    cursor.close()
    conn.close()
    return metrics


with DAG(
    dag_id="metrics_aggregation",
    default_args=DEFAULT_ARGS,
    description="Daily aggregation of clinical metrics for dashboards",
    schedule="0 4 * * *",
    start_date=datetime(2026, 1, 1),
    catchup=False,
    tags=["metrics", "dashboards"],
) as dag:

    aggregate = PythonOperator(
        task_id="aggregate_daily_metrics",
        python_callable=aggregate_daily_metrics,
    )
