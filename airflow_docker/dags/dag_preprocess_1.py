from io import BytesIO, StringIO
from src.data_preprocess_1 import preprocess_3
from datetime import datetime, timedelta
from sqlalchemy import create_engine
import psycopg2
from minio import Minio
from minio.error import S3Error
import pandas as pd

from airflow import DAG
from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook     # Reading the data from s3 and storing it locally
from airflow.providers.amazon.aws.hooks.s3 import S3Hook

default_args = {
    'owner': 'gauti',
    'retries': 5,
    'retry_delay': timedelta(minutes=5)
}

# Define the function to execute for pushing data
def data_retrieval_postgres():
    
    # step 1: query data from postgresql db and store it as dataframe
    hook = PostgresHook(postgres_conn_id="postgres_localhost")
    conn = hook.get_conn()
    cursor = conn.cursor()
    cursor.execute("select * from public.image_class")

    data = cursor.fetchall()  # Fetch all rows from the cursor

   # Extract column names
    column_names = [desc[0] for desc in cursor.description]

    # Create a DataFrame from the fetched data
    df_postgres = pd.DataFrame(data, columns=column_names)

    # Close the cursor and connection (important for resource management)
    cursor.close()
    conn.close()

    return df_postgres

# -------------------------------------------------------------------------------------------------

def data_retrieval_minio():
    # step 2: Load the data from minio
    # Retrieve S3 connection details from Airflow connections
    s3_hook = S3Hook(aws_conn_id='minio_conn_')

     # Define bucket name and object name (filename)
    bucket_name = "airflow-test" # Better to be created in Minio earlier
    object_name = "plant_data.csv"  # Replace with desired filename

    # Read data from S3
    data_string = s3_hook.read_key(key=object_name, bucket_name=bucket_name)

    # Convert data string to DataFrame (adjust format based on your data)
    df_minio = pd.read_csv(StringIO(data_string))

    return df_minio

# -------------------------------------------------------------------------------------------------

def data_preprocess_1():

    df_postgres = data_retrieval_postgres()
    df_minio = data_retrieval_minio()

    # Pass the dataframes for preprocessing
    image_norm_array, label, status_code = preprocess_3(df_postgres, df_minio)

    # Validate and then push the array to Minio
    if status_code == 200:

        config = {
        "minio_endpoint": "localhost:9000",
        "minio_username": "ROOTNAME",
        "minio_password": "CHANGEME123",
        }

        client = Minio(config["minio_endpoint"],
               secure=False,
               access_key=config["minio_username"],
               secret_key=config["minio_password"],
        )

        # Define bucket name and object name (filename)
        bucket_name = "airflow" # Better to be created in Minio earlier
        object_name = "airflow_testing/preprocess/image_preprocess_1.npy"  # Replace with desired filename
        object_name_1 = "airflow_testing/preprocess/label.csv"

        try:
            # Upload data to MinIO
            client.put_object(
                bucket_name=bucket_name, 
                object_name=object_name, 
                data=image_norm_array.tobytes(), 
                length=image_norm_array.nbytes,
                # content_type='application/csv'
                )

            # Optional: Log success message
            print(f"Successfully uploaded data to MinIO: {object_name}")

            # Convert DataFrame to CSV string (adjust based on your file format)
            csv_data = label.to_csv(index=False)
            csv_data_bytes = csv_data.encode('utf-8')  # Convert to bytes (adjust encoding if needed)
            csv_data_io = BytesIO(csv_data_bytes)  # Create BytesIO object

            # Upload data to MinIO
            client.put_object(
                bucket_name=bucket_name, 
                object_name=object_name_1, 
                data=csv_data_io, 
                length=len(csv_data),
                # content_type='application/csv'
                )

            # Optional: Log success message
            print(f"Successfully uploaded data to MinIO: {object_name_1}")

        except S3Error as e:
            print(f"Error occurred: {str(e)}")       
        
    else:
        print(f'Error: with {image_norm_array} status_code {status_code}')

# -------------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------------

# Define the DAG
with DAG(
    dag_id="dag_preprocess_1_v04",
    default_args=default_args,
    start_date=datetime(2024, 1, 25),
    schedule_interval='@yearly',  # Adjust as needed (e.g., hourly, @once)
) as dag:

    # Task to push data to the table
    pull_data_postgres_task = PythonOperator(
        task_id="pull_data_from_postgres",
        python_callable=data_retrieval_postgres,
        provide_context=True,  # Makes df available in the function
        execution_timeout=timedelta(minutes=60)  # Increase timeout if needed
    )

    pull_data_minio_task = PythonOperator(
        task_id="pull_data_from_minio",
        python_callable=data_retrieval_minio,
        provide_context=True,  # Makes df available in the function
    )

    datapreprocess1_minio_task = PythonOperator(
        task_id="data_preprocess1_minio",
        python_callable=data_preprocess_1,
        provide_context=True,  # Makes df available in the function
    )



    # Set up the task dependencies (create table first, then push data)
    pull_data_postgres_task >> pull_data_minio_task >> datapreprocess1_minio_task