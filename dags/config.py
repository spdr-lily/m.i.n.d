from datetime import timedelta
import os

DB_CONN_ID = "mind_postgres"
DEFAULT_ARGS = {
    "owner": "mind",
    "depends_on_past": False,
    "email_on_failure": True,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}
BATCH_SIZE = int(os.getenv("AIRFLOW_BATCH_SIZE", "100"))
