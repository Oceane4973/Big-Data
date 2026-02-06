import os
from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta

SPARK_MASTER_HOST=os.getenv("SPARK_MASTER_CONTAINER_NAME")

default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
}

with DAG(
    dag_id="big_data_tp_workflow",
    default_args=default_args,
    description="Ingestion API SNCF to Grafana Dashboard",
    schedule_interval="*/5 * * * *",
    start_date=datetime(2026, 1, 1),
    catchup=False,
    tags=["sncf"],
) as dag:
    ingest_task = BashOperator(
        task_id="fetch_sncf_data",
        bash_command="python /opt/airflow/src/extract_marseille_arrivals.py",
        execution_timeout=timedelta(minutes=10)
    )
    run_spark_job = BashOperator(
        task_id="spark_preprocess",
        bash_command=(
            "docker exec spark-master "
            "/opt/spark/bin/spark-submit "
            f"--master spark://{SPARK_MASTER_HOST}:7077 "
            "--packages org.mongodb.spark:mongo-spark-connector_2.13:11.0.0,org.postgresql:postgresql:42.7.9 "
            "--conf spark.jars.ivy=/opt/spark/ "
            "/opt/spark/jobs/preprocess.py"
        ),
        execution_timeout=timedelta(minutes=10)
    )

    ingest_task >> run_spark_job