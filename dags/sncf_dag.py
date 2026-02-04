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
    dag_id="sncf_to_mongo_datalake",
    default_args=default_args,
    description="Ingestion API SNCF vers MongoDB",
    schedule_interval="*/5 * * * *",  # Tous les jours 5 minutes
    start_date=datetime(2025, 1, 1),
    catchup=False,
    tags=["sncf", "datalake", "mongo"],
) as dag:

    ingest_task = BashOperator(
        task_id="fetch_sncf_data",
        bash_command="python ./src/extract.py"
    )

    ingest_task
