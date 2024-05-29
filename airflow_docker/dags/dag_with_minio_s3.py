from datetime import datetime, timedelta

from airflow import DAG
from airflow.providers.amazon.aws.sensors.s3 import S3KeySensor
default_args = {
    'owner': 'gauti',
    'retries': 5,
    'retry_delay': timedelta(minutes=5)
}

with DAG(
    dag_id='dag_with_minio_s3_v02',
    default_args=default_args,
    start_date=datetime(2024, 5, 10),
    schedule='@daily',   # replacement for @daily(0 0 * * *) only on friday at 2pm(0 14 * * Fri)
    
) as dag:
    task1 = S3KeySensor(
        task_id='sensor_minio_s3',
        bucket_name='airflow',
        bucket_key='data.csv',
        aws_conn_id='minio_conn',
        mode='poke',
        poke_interval=5,
        timeout=30
    )