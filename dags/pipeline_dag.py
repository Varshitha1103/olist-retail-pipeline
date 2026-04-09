from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import sys
sys.path.insert(0, '/path/to/olist_pipeline/src')
from etl import (extract_data, transform_data, 
                 load_data, run_quality_checks)

# Default settings for DAG
default_args = {
    'owner': 'varshitha',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5)
}

# Define the DAG
dag = DAG(
    'olist_retail_pipeline',
    default_args=default_args,
    description='Retail Order Delay Detection Pipeline',
    schedule_interval='@daily',
    catchup=False
)

# Define file path
DATA_PATH = '/path/to/Brazillian dataset'

def run_extraction():
    customers, orders, order_items, payments, products, sellers, category = extract_data(DATA_PATH)
    return "Extraction Done"

def run_transformation():
    customers, orders, order_items, payments, products, sellers, category = extract_data(DATA_PATH)
    fact_orders, orders_analysis = transform_data(
        customers, orders, order_items, 
        payments, products, sellers, category)
    return fact_orders, orders_analysis

def run_load():
    customers, orders, order_items, payments, products, sellers, category = extract_data(DATA_PATH)
    fact_orders, orders_analysis = transform_data(
        customers, orders, order_items,
        payments, products, sellers, category)
    load_data(fact_orders, orders_analysis)

def run_checks():
    customers, orders, order_items, payments, products, sellers, category = extract_data(DATA_PATH)
    fact_orders, orders_analysis = transform_data(
        customers, orders, order_items,
        payments, products, sellers, category)
    run_quality_checks(fact_orders)

# Define Tasks
task_extract = PythonOperator(
    task_id='extract_data',
    python_callable=run_extraction,
    dag=dag
)

task_transform = PythonOperator(
    task_id='transform_data',
    python_callable=run_transformation,
    dag=dag
)

task_load = PythonOperator(
    task_id='load_data',
    python_callable=run_load,
    dag=dag
)

task_quality = PythonOperator(
    task_id='quality_checks',
    python_callable=run_checks,
    dag=dag
)

# Define pipeline order
task_extract >> task_transform >> task_load >> task_quality