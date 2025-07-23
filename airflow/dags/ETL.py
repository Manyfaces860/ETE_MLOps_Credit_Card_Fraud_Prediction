import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from scripts.data_extract import DataIngestion
from scripts.data_transform import DataTransformation
from src.configuration.config_manager import ConfigurationManager
from src.logger import logging as logger
from src.utils.artifact_serializer import ArtifactSerializer
from airflow.operators.bash import BashOperator

import pendulum

from airflow.sdk import dag, task
from airflow.exceptions import AirflowException

@dag(
    schedule=None,
    start_date=pendulum.datetime(2021, 1, 1, tz="UTC"),
    catchup=False,
    tags=["example"],
    render_template_as_native_obj=True,
)
def extract_transform_load():


    @task()
    def extract():
        """
        #### Extract task
        A simple Extract task to get data ready for the rest of the data
        pipeline.
        """
        config_manager = ConfigurationManager()

        config = config_manager.get_data_ingestion_config()

        ob = DataIngestion(config)
        logger.info("Starting data ingestion process...")
        
        ingestion_artifact = ob.initiate_data_ingestion()
        
        if ingestion_artifact.status:
            logger.info("Data ingestion completed successfully")
        else:
            logger.error("Data ingestion failed")
            raise AirflowException("Data ingestion failed")
        
        return ArtifactSerializer.serialize(ingestion_artifact)
        
    dvc_version_raw_data_task = BashOperator(
        task_id="dvc_version_raw_data",
        bash_command=f"""
            cd /opt/airflow

            RAW_DATA_PATH="{{{{ ti.xcom_pull(task_ids='extract')['data_ingestion_unzip_file_path'] }}}}"
            COMMIT_MSG="DVC: Versioned raw data from $(basename $RAW_DATA_PATH)"
            
            ./dags/bash/dvc_track_raw_data.sh "$RAW_DATA_PATH" "$COMMIT_MSG"
        """,
    )


    @task()
    def transform(ingestion_artifact: dict):
        config_manager = ConfigurationManager()
        
        config = config_manager.get_data_transformation_config()
        ob = DataTransformation(config)
        logger.info("Starting data transformation process...") 
        ingestion_artifact = ArtifactSerializer.deserialize(ingestion_artifact)
        transformation_artifact = ob.initiate_data_transformation(ingestion_artifact)
        
        if transformation_artifact.status:
            logger.info("Data transformation completed successfully")
            return ArtifactSerializer.serialize(transformation_artifact)
        else:
            logger.error("Data transformation failed")
            raise AirflowException("Data transformation failed")
        
    load = BashOperator(
        task_id="load",
        bash_command=f"""
            cd /opt/airflow

            OBJ_PATH="{{{{ ti.xcom_pull(task_ids='transform')['transformed_object_file_path'] }}}}"
            DATA_PATH="{{{{ ti.xcom_pull(task_ids='transform')['transformed_file_path'] }}}}"
            
            COMMIT_MSG="DVC: Versioned transformed data and preprocessor object"
            
            ./dags/bash/dvc_load_task.sh "$OBJ_PATH" "$DATA_PATH" "$COMMIT_MSG"
        """,
    )
    
    # @task()
    # def load(total_order_value: float):
    #     """
    #     #### Load task
    #     A simple Load task which takes in the result of the Transform task and
    #     instead of saving it to end user review, just prints it out.
    #     """

    #     print(f"Total order value is: {total_order_value:.2f}")
    ingestion = extract()
    ingestion >> dvc_version_raw_data_task
    # logger.info(f"Data ingestion artifact: {ingestion}")
    
    transformation = transform(ingestion)
    dvc_version_raw_data_task >> transformation
    
    transformation >> load
    
    # logger.info(f"Data transformation artifact: {transformation}")
    # order_summary = transform(order_data)
    # load(order_summary["total_order_value"])
    
extract_transform_load()
