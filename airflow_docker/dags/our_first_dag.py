from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta


default_args = {
    'owner': 'gauti',
    'retries': 5,
    'retry_delay': timedelta(minutes=2)
}


with DAG(
    dag_id = "our_first_dag_v5",
    default_args= default_args,
    description = 'This is our first dag',
    start_date = datetime(2024, 5, 12, 2),
    schedule= '@daily'

) as dag:
    task1 = BashOperator(
        task_id = 'first_task',
        bash_command= 'echo hello everyone, this is our first task!!!'
    )

    task2 = BashOperator(
        task_id = 'second_task',
        bash_command = 'echo hai, I am newly created task 2 and I will run after the first task!'
    )

    task3 = BashOperator(
        task_id = 'third_task',
        bash_command = 'echo hey, I am task 3 and I will run after task1 but at the same time as task2....'
    )

    # Task dependency 1
    # task1.set_downstream(task2)
    # task1.set_downstream(task3)

    # Task dependency 2
    # task1 >> task2
    # task1 >> task3

    # Task dependency 3
    task1 = [task2, task3]
