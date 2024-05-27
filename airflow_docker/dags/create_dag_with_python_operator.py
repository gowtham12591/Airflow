from datetime import datetime, timedelta 

from airflow import DAG
from airflow.operators.python import PythonOperator

default_args = {
    'owner': 'gauti',
    'retries': 5,
    'retry_delay': timedelta(minutes=5)
}


def greet(name, age):
    print(f'Hello everyone, my name is {name},'
          f'and I am {age} years old!')
    
def get_name():
    return 'gowtham'


with DAG(
    default_args=default_args,
    dag_id='dag_python_operator_v03',
    description='our first dag using python operator',
    start_date=datetime(2024, 5, 22),
    schedule='@daily'

) as dag:
    
    # task1 = PythonOperator(
    #     task_id='greet',
    #     python_callable=greet,
    #     op_kwargs={'name': 'gauti', 'age': 30}
    # )

    task2 = PythonOperator(
        task_id='get_name',
        python_callable=get_name,
    )

    task2