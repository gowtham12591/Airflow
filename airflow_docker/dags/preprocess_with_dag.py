from io import BytesIO, StringIO
from src.data_preprocess import preprocess_1, preprocess_2
from src.data_preprocess_1 import preprocess_3, preprocess_4
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

from airflow import DAG
from airflow.operators.python import PythonOperator

default_args = {
    'owner': 'gauti',
    'retries': 5,
    'retry_delay': timedelta(minutes=5)
}

dataset_path = "/opt/airflow/dags/data"
storage_path = dataset_path + '/preprocess'

# Define the function to execute for pushing data
def data_preprocess_1():

    # pass the dataset and get extract the images in the form of dataframe
    df_image, status_code = preprocess_1(dataset_path)

    if status_code == 200:
        # Save the dataframes for future use
        df_image.to_csv(storage_path + '/image_data.csv', index=False)
        # return df_image

    else:
        print(f' error: {df_image}')

# -------------------------------------------------------------------------------------------------

def data_preprocess_2():

    data_path = storage_path + '/' + 'image_data.csv'
    processed_image, labels, test_dataset, status_code = preprocess_2(data_path)

    if status_code == 200:
        # Save the dataframes for future use
        np.save(storage_path + '/image_data_processed_1.npy', processed_image, allow_pickle=True)
        np.save(storage_path + '/label_array.npy',labels, allow_pickle=True)
        test_dataset.to_csv(storage_path + '/test_dataframe.csv', index=False)
        # return processed_image, labels

    else:
        print(f' error: {processed_image, labels}')

# -------------------------------------------------------------------------------------------------

def data_preprocess_3():

    data_path = storage_path + '/' + 'image_data_processed_1.npy'
    lables_path = storage_path + '/' + 'label_array.npy'
    preprocessed_images, preprocessed_labels, status_code = preprocess_3(data_path, lables_path)   

    if status_code == 200:
        # Save the dataframes for future use
        np.save(storage_path + '/augmented_images_data.npy', preprocessed_images, allow_pickle=True)
        np.save(storage_path + '/augmented_labels_data.npy',preprocessed_labels, allow_pickle=True)
        
        # return processed_images, preprocessed_labels

    else:
         print(f' error: {preprocessed_images, preprocessed_labels}')

# -------------------------------------------------------------------------------------------------
    
def data_preprocess_4():

    data_path = storage_path + '/' + 'augmented_images_data.npy'
    preprocessed_image_norm, preprocessed_image_std, status_code = preprocess_4(data_path)   

    if status_code == 200:
        # Save the dataframes for future use
        np.save(storage_path + '/normalized_image_data.npy', preprocessed_image_norm, allow_pickle=True)
        np.save(storage_path + '/standardized_image_data.npy',preprocessed_image_std, allow_pickle=True)
        
        # return processed_image_norm, preprocessed_image_std

    else:
         print(f' error: {preprocessed_image_norm, preprocessed_image_std}')
    
# -------------------------------------------------------------------------------------------------

# Define the DAG
with DAG(
    dag_id="preprocess_with_dag_v01",
    default_args=default_args,
    start_date=datetime(2024, 1, 25),
    schedule_interval='@daily',  # Adjust as needed (e.g., hourly, @once)
) as dag:

    # Task to push data to the table
    image_extraction = PythonOperator(
        task_id="image_extraction",
        python_callable=data_preprocess_1,
        provide_context=True,  # Makes df available in the function
        # execution_timeout=timedelta(minutes=60)  # Increase timeout if needed
    )

    image_preprocessing = PythonOperator(
        task_id="image_preprocessing",
        python_callable=data_preprocess_2,
        provide_context=True,  # Makes df available in the function
    )

    image_augmentation = PythonOperator(
        task_id="image_augmentation",
        python_callable=data_preprocess_3,
        provide_context=True,  # Makes df available in the function
    )

    image_scaling = PythonOperator(
        task_id="image_scaling",
        python_callable=data_preprocess_4,
        provide_context=True,  # Makes df available in the function
    )



    # Set up the task dependencies (create table first, then push data)
    image_extraction >> image_preprocessing >> image_augmentation >> image_scaling