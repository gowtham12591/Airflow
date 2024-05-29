from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.bash import BashOperator

default_args = {
    'owner': 'gauti',
    'retries': 5,
    'retry_delay': timedelta(minutes=5)
}

with DAG(
    dag_id='dag_with_cron_expression_v04',
    default_args=default_args,
    start_date=datetime(2024, 5, 10),
    schedule='0 14 * * Mon-Wed,Fri',   # replacement for @daily(0 0 * * *) only on friday at 2pm(0 14 * * Fri)
    
) as dag:
    task1 = BashOperator(
        task_id='task1',
        bash_command='echo This is a testing cron job expressions!!!'

    )

    # website for understanding cron job https://crontab.guru/
    # 0 14 * * Mon-Wed,Fri - Monday to wednesday and friday of every week at 2pm