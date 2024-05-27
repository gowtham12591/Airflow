from datetime import datetime, timedelta 

from airflow import DAG
from airflow.operators.python import PythonOperator

default_args = {
    'owner': 'gauti',
    'retries': 5,
    'retry_delay': timedelta(minutes=5)
}


def greet(ti):
    first_name = ti.xcom_pull(task_ids='get_name', key='first_name')
    last_name = ti.xcom_pull(task_ids='get_name', key='last_name')
    age_ = ti.xcom_pull(task_ids='get_age', key='age_')
    print(f'Hey everyone , My name is {first_name} {last_name}'
          f' and my age is {age_} years old!!!')

    
def get_name(ti):
    ti.xcom_push(key='first_name', value='gowtham')
    ti.xcom_push(key='last_name', value='swamy')

def get_age(ti):
    ti.xcom_push(key='age_', value='30')
    

with DAG(
    default_args=default_args,
    dag_id='dag_python_operator_v07',
    description='our second dag using python operator',
    start_date=datetime(2024, 5, 22),
    schedule='@daily'

) as dag:
    
    task1 = PythonOperator(
        task_id='greet',
        python_callable=greet,
    )

    task2 = PythonOperator(
        task_id='get_name',
        python_callable=get_name,
    )

    task3 = PythonOperator(
        task_id='get_age',
        python_callable=get_age,
    )

    [task2, task3] >> task1