from datetime import datetime, timedelta
import csv
import logging
from tempfile import NamedTemporaryFile   # storing the data temporarily in local

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook     # Reading the data from s3 and storing it locally
from airflow.providers.amazon.aws.hooks.s3 import S3Hook               # Uploading the data to s3

default_args = {
    'owner': 'gauti',
    'retries': 5,
    'retry_delay': timedelta(minutes=5)
}

def postgres_to_s3(ds_nodash, next_ds_nodash):
    # step 1: query data from postgresql db
    hook = PostgresHook(postgres_conn_id="postgres_localhost")
    conn = hook.get_conn()
    cursor = conn.cursor()
    cursor.execute("select * from orders where date >= %s and date < %s", (ds_nodash, next_ds_nodash))
    with NamedTemporaryFile(mode='w', suffix=f'{ds_nodash}') as f:
    # with open(f"dags/get_orders_{ds_nodash}.txt", "w") as f:
        csv_writer = csv.writer(f)
        csv_writer.writerow([i[0] for i  in cursor.description])
        csv_writer.writerows(cursor)
        f.flush()
        cursor.close()
        conn.close()
        logging.info('saved orders data in text file: %s', f"dags/get_orders_{ds_nodash}.txt")

    # step 2: uploading the text file to s3 bucket
        s3_hook = S3Hook(aws_conn_id="minio_conn_")
        s3_hook.load_file(
            filename=f.name,
            key=f'orders/{ds_nodash}.txt',
            bucket_name='airflow',
            replace=True
        )
        logging.info('Orders file %s has been pushed to S3', f.name)

with DAG(
    dag_id='dag_with_postgres_hooks_v07',
    default_args=default_args,
    start_date=datetime(2022, 1, 1),
    end_date=datetime(2023, 1, 1),
    schedule='@monthly',   # replacement for @daily(0 0 * * *) only on friday at 2pm(0 14 * * Fri)
    
) as dag:
    task1 = PythonOperator(
        task_id='postgres_to_s3',
        python_callable=postgres_to_s3

    )   