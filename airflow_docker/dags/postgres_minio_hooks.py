
from io import BytesIO
from src.image_process_ import image_extract
from datetime import datetime, timedelta
from sqlalchemy import create_engine
import psycopg2
from minio import Minio
from minio.error import S3Error

from airflow import DAG
from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow.operators.python import PythonOperator
from airflow.providers.amazon.aws.hooks.s3 import S3Hook 


# Define connection details (replace with your actual credentials)
POSTGRES_CONN_ID = "postgres"
POSTGRES_TABLE_NAME = "public.image_class"

dataset_path = "/opt/airflow/dags/data"

default_args = {
    'owner': 'gauti',
    'retries': 5,
    'retry_delay': timedelta(minutes=5)
}

# Define the function to execute for pushing data
def push_data_to_postgres():
    # Get the dataframe from image_extract file
    df_postgres, df_minio, status_code = image_extract(dataset_path)

    if status_code == 200:

        # Connect to Postgres using SQLAlchemy and psycopg2
        
        engine = create_engine(
            f"postgresql://airflow:airflow@host.docker.internal:5432/{POSTGRES_CONN_ID}",
        )

        # Insert data into the table using pandas.to_sql
        df_postgres.to_sql(POSTGRES_TABLE_NAME, engine, if_exists='replace', index=False)

    else:
        print(f'Error: {df_postgres} with status_code {status_code}')

def push_data_to_minio_task(ds_nodash):
    # Get the dataframe from image_extract file
    df_postgres, df_minio, status_code = image_extract(dataset_path)

        # Get MinIO connection details from Airflow connections
        # minio_connection = AIRFLOW.get_connection('minio_connection')
    if status_code == 200:

        # Create S3Hook using MinIO connection details (might not be fully compatible)
        s3_hook = S3Hook(aws_conn_id='minio_conn')

        # Convert DataFrame to CSV string (adjust based on your file format)
        csv_data = df_minio.to_csv(index=False)
        # csv_data_bytes = csv_data.encode('utf-8')  # Convert to bytes (adjust encoding if needed)
        # csv_data_io = BytesIO(csv_data_bytes)  # Create BytesIO object

        # Define bucket name and object name (filename)
        bucket_name = "airflow"
        object_name = f"plant_data/{ds_nodash}.csv"  # Replace with desired filename

        try:
            # Upload data to MinIO
            s3_hook.load_string(
                bucket_name=bucket_name, 
                key=object_name, 
                string_data=csv_data, 
                # length=len(csv_data),
                # content_type='application/csv'
                )

            # Optional: Log success message
            print(f"Successfully uploaded data to MinIO: {object_name}")

        except S3Error as e:
            print(f"Error occurred: {str(e)}")

    else:
        print(f'Error: {df_minio} with status_code {status_code}')

# Define the DAG
with DAG(
    dag_id="postgres_minio_hooks_dag_v01",
    default_args=default_args,
    start_date=datetime(2024, 1, 25),
    schedule_interval='@yearly',  # Adjust as needed (e.g., hourly, @once)
) as dag:

    # Task to create the table (optional, can be run manually if the table already exists)
    create_table_task = PostgresOperator(
        task_id="create_table",
        postgres_conn_id='postgres_localhost',
        autocommit=True,
        sql="""
        CREATE TABLE IF NOT EXISTS public.image_class (
        image_id serial,
        filename varchar primary key,
        class varchar
        );
        """,
        # templates_dict={"table_name": POSTGRES_TABLE_NAME}
    )

    # Task to push data to the table
    push_data_postgres_task = PythonOperator(
        task_id="push_data_to_postgres",
        python_callable=push_data_to_postgres,
        provide_context=True,  # Makes df available in the function
        execution_timeout=timedelta(minutes=60)  # Increase timeout if needed
    )

    push_data_minio_task = PythonOperator(
        task_id="push_data_to_minio",
        python_callable=push_data_to_minio_task,
        provide_context=True,  # Makes df available in the function
    )

    # Set up the task dependencies (create table first, then push data)
    create_table_task >> push_data_postgres_task >> push_data_minio_task
