from airflow.decorators import dag, task
from airflow.operators.python import PythonOperator
from pendulum import datetime, timedelta


@dag(start_date=datetime(2025, 1, 1),
     schedule="@daily",
     catchup=False,
     description="This DAG processes e-commerce data",
     tags=['team_a', 'ecom'],
     default_args={
         'retries': 1
     },
     dagrun_timeout=timedelta(minutes=20),
     max_consecutive_failed_dag_runs=2)
def ecom():
    
    


ecom()