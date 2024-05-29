from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.bash import BashOperator

default_args = {
    'owner': 'gauti',
    'retries': 5,
    'retry_delay': timedelta(minutes=5)
}

with DAG(
    dag_id='dag_with_catchup_backfill_v02',
    default_args=default_args,
    start_date=datetime(2024, 5, 20),
    schedule='@daily',
    catchup=False,
) as dag:
    task1 = BashOperator(
        task_id='task1',
        bash_command='echo This is a test bash command!!!'

    )

# By setting catchup=False the dags will run only on the current date and it will not run the previous dates(catchup)
# If we want to run the previous days dags then we can use backfill option
# In the terminal window run docker ps command
# collect the container id of airflow scheduler and then use the command
#    docker exec -it <container_id> bash

# It will open the container, there we can use the command
#    airflow dags backfill -s 2024-5-20 -e 2024-5-26 dag_with_catchup_backfill_v02
# we can mention the dates for the backfill which will run the older dates dags
# we can exit the terminal using the command exit
# Once you refresh the browser you can see the changes