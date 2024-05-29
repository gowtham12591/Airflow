from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python import PythonOperator

default_args = {
    'owner': 'gauti',
    'retries': 5,
    'retry_delay': timedelta(minutes=5)
}

def get_sklearn():
    import sklearn
    print(f'scikit-learn version {sklearn.__version__}')

def get_matplotlib():
    import matplotlib
    print(f'Matplotlib version {matplotlib.__version__}')

with DAG(
    dag_id='dag_with_python_dependencies_v02',
    default_args=default_args,
    start_date=datetime(2024, 5, 10),
    schedule='@daily',   # replacement for @daily(0 0 * * *) only on friday at 2pm(0 14 * * Fri)
    
) as dag:
    
    get_sklearn = PythonOperator(
        task_id='get_sklearn',
        python_callable=get_sklearn,
    )

    get_matplotlib = PythonOperator(
        task_id='get_matplotlib',
        python_callable=get_matplotlib,
    )

    get_sklearn >> get_matplotlib