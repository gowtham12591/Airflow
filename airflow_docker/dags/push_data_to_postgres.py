import sys
sys.path.append("/Users/gowtham/Documents/python/SCB/airflow/airflow_docker/src")

from dags.src.image_process_ import image_extract
from datetime import datetime, timedelta
from sqlalchemy import create_engine
import psycopg2

from airflow import DAG
from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow.operators.python import PythonOperator


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
    # Replace with your logic to get/create the DataFrame (df)

    df, df1, status_code = image_extract(dataset_path)

    if status_code == 200:

        # Connect to Postgres using SQLAlchemy and psycopg2
        
        engine = create_engine(
            f"postgresql://airflow:airflow@host.docker.internal:5432/{POSTGRES_CONN_ID}",
        )

        # Convert DataFrame to a list of dictionaries (optimized for bulk inserts)
        # df_records = [dict(row) for row in df.itertuples()]

        # Insert data into the table using psycopg2 (more efficient for bulk inserts)

        # with psycopg2.connect(
        #     dbname=POSTGRES_CONN_ID, user="airflow", password="airflow", host="host.docker.internal"
        # ) as conn:
        #     with conn.cursor() as cur:
        #         # Assuming your table schema matches the DataFrame columns
        #         insert_query = f"INSERT INTO {POSTGRES_TABLE_NAME} ({','.join(df.columns)}) VALUES %s"
        #         cur.executemany(insert_query, df_records)
        #         conn.commit()

        # Alternatively, you could use pandas.to_sql (might be slower for large datasets)

        # Insert data into the table using pandas.to_sql
        df.to_sql(POSTGRES_TABLE_NAME, engine, if_exists='replace', index=False)

    else:
        print(f'Error: {df} with status_code {status_code}')

# Define the DAG
with DAG(
    dag_id="push_data_to_postgres_dag_v2",
    default_args=default_args,
    start_date=datetime(2024, 5, 25),
    schedule_interval='@monthly',  # Adjust as needed (e.g., hourly, @once)
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
    push_data_task = PythonOperator(
        task_id="push_data",
        python_callable=push_data_to_postgres,
        provide_context=True,  # Makes df available in the function
        execution_timeout=timedelta(minutes=60)  # Increase timeout if needed
    )



# Set up the task dependencies (create table first, then push data)
create_table_task >> push_data_task
