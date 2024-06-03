from io import BytesIO, StringIO
from dags.src.data_preprocess_1 import image_preprocess_1
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
    cursor.execute("select * from image_class")

    data = cursor.fetchall()  # Fetch all rows from the cursor

    # Create a DataFrame from the fetched data
    df_postgres = pd.DataFrame(data, columns=[col_name for col_name in cursor.description])

    # Close the cursor and connection (important for resource management)
    cursor.close()
    conn.close()

    return df_postgres

# -------------------------------------------------------------------------------------------------

def data_retrieval_minio():
    # step 2: Load the data from minio
    # Retrieve S3 connection details from Airflow connections
    s3_hook = S3Hook(aws_conn_id='minio_conn')

     # Define bucket name and object name (filename)
    bucket_name = "airflow" # Better to be created in Minio earlier
    object_name = "plant_data.csv"  # Replace with desired filename

    # Download data from S3
    data_bytes = s3_hook.download_file(bucket_name=bucket_name, key=object_name)

    # Decode data based on encoding used when uploading (e.g., utf-8)
    data_string = data_bytes.decode('utf-8')

    # Convert data string to DataFrame (adjust format based on your data)
    df_minio = pd.read_csv(StringIO(data_string))

    return df_minio

# -------------------------------------------------------------------------------------------------

def data_preprocess_1():

    df_postgres = data_retrieval_postgres()
    df_minio = data_retrieval_minio()

    # Pass the dataframes for preprocessing
    image_norm_array, status_code = image_preprocess_1(df_postgres, df_minio)

    # Validate and then push the array to Minio
    if status_code == 200:

        config = {
        "minio_endpoint": "host.docker.internal:9000",
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
        object_name = "image_preprocess_1.npy"  # Replace with desired filename

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

        except S3Error as e:
            print(f"Error occurred: {str(e)}")       
        
    else:
        print(f'Error: with {image_norm_array} status_code {status_code}')