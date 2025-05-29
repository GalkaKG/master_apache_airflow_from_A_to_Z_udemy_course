from airflow.decorators import dag, task, task_group
from airflow.operators.python import PythonOperator
from pendulum import datetime, duration
from include.datasets import DATASET_COCKTAIL
from include.tasks import _get_cocktail, _check_size, _validate_cocktail_fields
from include.extractor.callbacks import _handle_failed_dag_run, _handle_empty_size
import json
from airflow.utils.trigger_rule import TriggerRule


@dag(
    start_date=datetime(2025, 1, 1),
    schedule='@daily',
    default_args={
        'retries': 2,
        'retry_delay': duration(seconds=2),
    },
    tags=['ecom'],
    catchup=False,
    on_failure_callback=_handle_failed_dag_run,
)
def extractor():
    
    get_cocktail = PythonOperator(
        task_id='get_cocktail',
        python_callable=_get_cocktail,
        outlets=[DATASET_COCKTAIL],
        retry_exponential_backoff=True,
        max_retry_delay=duration(minutes=15)
    )

    @task_group
    def checks():

        check_size = PythonOperator(
            task_id='check_size',
            python_callable=_check_size,
            on_failure_callback=_handle_empty_size,
        )

        validate_fields = PythonOperator(
            task_id='validate_fields',
            python_callable=_validate_cocktail_fields
        ) 

        check_size >> validate_fields

    # def store_value(ti=None):
    #     ti.xcom_pull(task_ids="checks.validate_fields")

    @task.branch()
    def branch_cocktail_type():
        with open(DATASET_COCKTAIL.uri, 'r') as f:
            data = json.load(f)
        if data['drinks'][0]['strAlcoholic'] == 'Alcoholic':
            return 'alcoholic_cocktail'
        return 'non_alcoholic_cocktail'
    
    @task()
    def alcoholic_cocktail():
        print('Alcoholic cocktail found!')

    @task()
    def non_alcoholic_cocktail():
        print('Non-alcoholic cocktail found!')

    @task(trigger_rule=TriggerRule.NONE_FAILED_MIN_ONE_SUCCESS)
    def clean_data():
        import os
        if os.path.exists(DATASET_COCKTAIL.uri):
            os.remove(DATASET_COCKTAIL.uri)
        else:
            print(f"{DATASET_COCKTAIL.uri} does not exist")

    get_cocktail >> checks() >> branch_cocktail_type() >> [alcoholic_cocktail(), non_alcoholic_cocktail()] >> clean_data()
    
my_extractor = extractor()

if __name__ == "__main__":
    my_extractor.test()  