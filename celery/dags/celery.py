from airflow.decorators import dag, task
from pendulum import datetime
from time import sleep

@dag(start_date=datetime(2025, 1, 1), schedule=None, catchup=False)
def celery():

    @task
    def a(queue='cpu'):
        print('A')
        sleep(15)
    
    @task
    def b(queue='gpu'):
        print('B')
        sleep(15)

    @task
    def c(queue='cpu'):
        print('C')
        sleep(15)

    @task
    def d(queue='cpu'):
        print('D')
        sleep(15)

    @task
    def e():
        print('E')
        sleep(15)

    a() >> [b(), c() >> d() >> e()]

celery()