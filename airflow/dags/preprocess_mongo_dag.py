from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta

default_args = {
    "owner": "airflow",
    "retries": 1,
    "retry_delay": timedelta(minutes=2),
}

with DAG(
    dag_id="mongo_datalake_to_postgres",
    default_args=default_args,
    description="Preprocessing Mongo datalake to Postrges",
    schedule_interval="*/5 * * * *",
    start_date=datetime(2026, 1, 1),
    catchup=False,
    tags=["sncf", "datalake", "mongo"],
) as dag:
    run_spark_job = BashOperator(
        task_id="spark_preprocess",
        bash_command="docker exec spark-master /opt/spark/bin/spark-submit --master spark://spark-master:7077 /opt/spark/jobs/preprocess.py"
    )

    run_spark_job
