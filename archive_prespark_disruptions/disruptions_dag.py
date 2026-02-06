from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta

default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
}

with DAG(
    dag_id="mongo_to_postgre",
    default_args=default_args,
    description="Traitement données MongoDB vers Postgre",
    schedule_interval="*/5 * * * *",  # Toutes les 5 minutes
    start_date=datetime(2026, 1, 1),
    catchup=False,
    tags=["mongo", "postgre"],
) as dag:
    ingest_task = BashOperator(
        task_id="process_disruptions_data",
        bash_command="python /opt/airflow/src/process_disruptions.py"
    )

    ingest_task
