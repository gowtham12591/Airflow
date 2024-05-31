Install airflow with docker .yml file
Visit the below page for installation details
https://airflow.apache.org/docs/apache-airflow/stable/howto/docker-compose/index.html

Once you have downloaded the .yml file using the command
  curl -LfO 'https://airflow.apache.org/docs/apache-airflow/2.9.1/docker-compose.yaml'

You can create the directories for logs, dags and plugins using the command
  mkdir -p ./dags ./logs ./plugins ./config

We need to make our airflow suitable for running in local system, so open the yml file and then remove wherever the celery part of the code, along with flowers package code comes, ref: https://www.youtube.com/watch?v=K9AnJ9_ZAXE&list=PLwFJcsJ61oujAqYpMp1kdUBcPG0sE0QMT
At the beginning of the yml file replace the below line
  AIRFLOW**CORE**EXECUTOR: LocalExecutor

You can now initialise the docker using the command
  docker-compose up airflow-init

Once the command is executed, then detach the docker to run the airflow server, scheduler, db etc using the command
  docker compose up -d

You can now use the command to see the airflow server, scheduler and db status
  docker ps

Now open the webbrowser using and navigate to 'http://127.0.0.1:8080' to see the example dags runnning

We can now remove the examples by shutting the docker and then repalce the line to false in the yml file
  AIRFLOW**CORE**LOAD_EXAMPLES: 'false'
  docker-compose down -v

Now bring back the docker to up-state using the below commands
docker-compose up airflow-init
docker-compose up -d

If we need to connect to postgres database

- Install postgresql in your system
- Install DBeaver
- Open docker-compose.yml file in our project directory and then add the port as mentioned below inside the postgres command after volumes
  ports: 
    - 5432:5432

- Now in the terminal run the below command to initalize the database
  docker-compose up -d --no-deps --build postgres

- Now open dbeaver and then click on database and then click new-database connection and then enter username and password as airflow and then check the testconnection
- Once connected, we can create new database and then create tables with airflow
- In the airflow webbrowser, open connection from admin and then create a connection with the database
 conn id: postgres_localhost
 conn type: postgres
 host: host.docker.internal
 schema: test
 login and pass: same as airflow login
 port: 5432


Installing python dependencies
- Extend method 
  - create a docker file and add the requirments
  - Now build the docker image using the command 
    docker build . --tag extending_airflow:latest
  - After the build is successful, change the image in docker-compose.yml file to -extending_airflow:latest (line 52)
  - We can test it with an example dags file
  - After adding the code in the file, before testing, we have rebuild the docker airflow images using
    docker-compose up -d --no-deps --build airflow-webserver airflow-scheduler
  - Whenever we add anymore requirements, we need to rebuild our docker image and the airflow containers for the reflection in webserver(UI)
- Customizing the image method
  - In a new folder clone the repo of official git repo from airflow
  - Inside the docker-context-files folder, create a new file requirements.txt
  - Add necessary packages and then build the image using the command
    docker build . --build-arg AIRFLOW_VERSION='2.9.1' --tag customising_airflow:latest
  - Now we can change the docker image in our current docker-compose.yml file to customising_airflow:latest
  - Now rebuild the docker airflow images using
    docker-compose up -d --no-deps --build airflow-webserver airflow-scheduler

MINIO installation with docker and its usage as a storage similar to AWS S3
- Visit this website (https://min.io/docs/minio/container/index.html?ref=docs-redirect) to get the docker command for running the minio
  mkdir -p ~/minio/data
  docker run \
    -p 9000:9000 \
    -p 9001:9001 \
    --name minio \
    -v ~/minio/data:/data \
    -e "MINIO_ROOT_USER=ROOTNAME" \
    -e "MINIO_ROOT_PASSWORD=CHANGEME123" \
    quay.io/minio/minio server /data --console-address ":9001"
- To run the above docker command open a seperate termianl in the vs code and then run it. 
- once the docker command is executed you can get the server for minio
  http://127.0.0.1:9001
- Go to the above link and then enter the username and password mentioned in the docker command
- After login then click on the create bucket icon and then give whatever the nema you want (airflow) and create it, check whether we have both read and right permission for the created bucket.
- After this we can either add the path of the file or upload a file
- In the code which we are using for connecting to minio we will use aws s3 api, as it is compatible to minio and available for airflow
- Before running the code, if we have changed the image on the yml file, then we need to recreate the docker image for airflow-webserver and airflow-scheduler using the command
  docker-compose up -d --no-deps --build airflow-webserver airflow-scheduler
- use the command docker ps to find the container id for the recreated iamge
- Now copy the container id of the docker image of airflow schduler which we want to use and execute the command
  docker exec -it <container_id> bash
- With the above command we will move inside that container, now run the command
  pip list | grep amazon
  we will get the apache airflow package of amazon along with its version
  ** Instead of amazon, if you give whatever the package name we can find the version for it, example postgres to see the installed version
- Now visit the below url and copy the class name and add it to the code in the import part
  https://airflow.apache.org/docs/apache-airflow-providers-amazon/8.20.0/_api/airflow/providers/amazon/aws/sensors/s3/index.html
- Now to establish a connection with s3, go the airflow web-browser and in admins click on connection and then add new connection
- Give connection_id similar to the code in dags and then connection_type as Amazon Web Services and in extra add the below code and save it
  {"aws_access_key_id":"ROOTNAME","aws_secret_access_key":"CHANGEME123","host":"http://host.docker.internal:9000"}