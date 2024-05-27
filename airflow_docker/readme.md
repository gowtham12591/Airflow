Install airflow with docker .yml file
Visit the below page for installation details
https://airflow.apache.org/docs/apache-airflow/stable/howto/docker-compose/index.html

Once you have downloaded the .yml file using the command
    curl -LfO 'https://airflow.apache.org/docs/apache-airflow/2.9.1/docker-compose.yaml'

You can create the directories for logs, dags and plugins using the command
    mkdir -p ./dags ./logs ./plugins ./config

We need to make our airflow suitable for running in local system, so open the yml file and then remove wherever the celery part of the code, along with flowers package code comes, ref: https://www.youtube.com/watch?v=K9AnJ9_ZAXE&list=PLwFJcsJ61oujAqYpMp1kdUBcPG0sE0QMT
At the beginning of the yml file replace the below line
    AIRFLOW__CORE__EXECUTOR: LocalExecutor

You can now initialise the docker using the command
    coker-compose up airflow-init

Once the command is executed, then detach the docker to run the airflow server, scheduler, db etc using the command
    docker compose up -d

You can now use the command to see the airflow server, scheduler and db status 
    docker ps

Now open the webbrowser using and navigate to 'http://127.0.0.1:8080' to see the example dags runnning

We can now remove the examples by shutting the docker and then repalce the line to false in the yml file
    AIRFLOW__CORE__LOAD_EXAMPLES: 'false'
    docker-compose down -v

Now bring back the docker to up-state using the below commands
    docker-compose up airflow-init
    airflow_docker % docker-compose up -d
