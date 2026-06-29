from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.databricks.operators.databricks import DatabricksRunNowOperator
from datetime import datetime
import sys
import os

include_path = os.path.join(os.environ.get('AIRFLOW_HOME', '/usr/local/airflow'), 'include')
sys.path.append(include_path)
from get_file_monthly import get_latest_vcv_clinvar_data

with DAG(
    dag_id='clinvar_ingestion_v1',
    start_date=datetime(2026, 3, 1),
    schedule_interval='0 0 1-7 * 5',
    catchup=False
) as dag:

    get_file_monthly = PythonOperator(
        task_id='get_file_monthly',
        python_callable=get_latest_vcv_clinvar_data
    )
    bronze_notebook = DatabricksRunNowOperator(
        task_id='bronze_notebook',
        databricks_conn_id='databricks_default',
        job_id=21292785076068
    )
    silver_notebook = DatabricksRunNowOperator(
        task_id='silver_notebook',
        databricks_conn_id='databricks_default',
        job_id=85643435147584
    )
    gold_notebook = DatabricksRunNowOperator(
        task_id='gold_notebook',
        databricks_conn_id='databricks_default',
        job_id=1035569646380529
    )

    get_file_monthly >> bronze_notebook >> silver_notebook >> gold_notebook