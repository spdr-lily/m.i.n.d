from datetime import datetime, timedelta
from textwrap import dedent

from airflow import DAG
from airflow.operators.python import PythonOperator, BranchPythonOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.operators.dummy import DummyOperator
from airflow.models import Variable

from dags.config import DEFAULT_ARGS, DB_CONN_ID, BATCH_SIZE


def fetch_pending_consultations(**context) -> list:
    hook = PostgresHook(postgres_conn_id=DB_CONN_ID)
    conn = hook.get_conn()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT consultation_uuid, profile_uuid
        FROM clinical.clinical_consultation
        WHERE inference_status = 'pending'
        ORDER BY created_at
        LIMIT %s
    """, (BATCH_SIZE,))
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    context["ti"].xcom_push(key="pending_consultations", value=rows)
    return rows


def run_bayesian_inference(consultation_uuid: str, profile_uuid: str, **context) -> dict:
    from app.ml.bayesian_inference_service import BayesianInferenceService
    from app.ml.network_definition import build_mood_disorder_network
    from sqlalchemy import create_engine
    from sqlalchemy.orm import Session

    bn = build_mood_disorder_network()
    engine = create_engine(Variable.get("database_url"))
    session = Session(engine)

    service = BayesianInferenceService(session, bn)
    result = service.infer_from_consultation(consultation_uuid)
    service.persist_inferences(consultation_uuid, result)

    session.close()
    engine.dispose()
    return {
        "consultation_uuid": consultation_uuid,
        "inferences": len(result),
    }


def batch_inference(**context) -> list:
    pending = context["ti"].xcom_pull(task_ids="fetch_pending")
    if not pending:
        return {"processed": 0, "message": "No pending consultations"}
    results = []
    for consultation_uuid, profile_uuid in pending:
        result = run_bayesian_inference(consultation_uuid, profile_uuid)
        results.append(result)
    return {"processed": len(results), "details": results}


def check_pending(**context) -> str:
    pending = context["ti"].xcom_pull(task_ids="fetch_pending")
    if not pending:
        return "skip_inference"
    return "run_inference"


with DAG(
    dag_id="clinical_inference_pipeline",
    default_args=DEFAULT_ARGS,
    description="Nightly batch Bayesian inference for pending consultations",
    schedule="0 2 * * *",
    start_date=datetime(2026, 1, 1),
    catchup=False,
    tags=["clinical", "inference"],
) as dag:

    start = DummyOperator(task_id="start")

    fetch = PythonOperator(
        task_id="fetch_pending",
        python_callable=fetch_pending_consultations,
    )

    branch = BranchPythonOperator(
        task_id="check_pending",
        python_callable=check_pending,
    )

    skip = DummyOperator(task_id="skip_inference")

    run = PythonOperator(
        task_id="run_inference",
        python_callable=batch_inference,
    )

    end = DummyOperator(task_id="end")

    start >> fetch >> branch
    branch >> skip >> end
    branch >> run >> end
