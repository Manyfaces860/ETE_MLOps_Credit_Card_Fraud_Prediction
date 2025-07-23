import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import datetime
from scripts.drift_detect import DataDrift
from scripts.model_trainer import ModelTrainer
from scripts.model_evalpush import ModelEvalPush
from src.configuration.config_manager import ConfigurationManager
from src.logger import logging as logger
from src.utils.artifact_serializer import ArtifactSerializer
from airflow.operators.bash import BashOperator
import dagshub
import mlflow
import pendulum

from airflow.sdk import dag, task
from airflow.exceptions import AirflowException

@dag(
    schedule=None,
    start_date=pendulum.datetime(2021, 1, 1, tz="UTC"),
    catchup=False,
    render_template_as_native_obj=True,
)
def drift_model_training():

    run_name = None
    experiment_name = None
    experiment_id = None
    run_id = None
    

    @task.branch()
    def drift_check(**kwargs):
        
        nonlocal run_name
        nonlocal experiment_name
        nonlocal experiment_id
        nonlocal run_id
        
        execution_date_str = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        run_name = f"drift_check_{execution_date_str}"
        experiment_name = f"experiment_{execution_date_str}"

        config_manager = ConfigurationManager()

        config = config_manager.get_data_drift_config()

        ob = DataDrift(config, run_name=run_name, experiment_name=experiment_name)
        logger.info("Starting data ingestion process...")
        
        trigger_flag, report_path = ob.detect_dataset_drift()
        dagshub.init(repo_owner='mynewdbdatabase',
                    repo_name='mlflowfor',
                    mlflow=True)
        
        
        experiment_id = mlflow.create_experiment(experiment_name)
        with mlflow.start_run(experiment_id=experiment_id) as run:            
            # Log the HTML report under the 'evidently_reports' artifact path
            mlflow.log_artifact(report_path, "evidently_report")
            run_id = run.info.run_id
            
            logger.info(f"Evidently AI HTML report logged as artifact: report.yml at {datetime.datetime.now()}")
        
        logger.info(f"Drift check completed with flag: {trigger_flag}")
        return trigger_flag
    
    @task()
    def model_train():
        nonlocal run_name
        nonlocal experiment_id
        nonlocal experiment_name
        nonlocal run_id
        
        logger.info("Model training task triggered.")

        config_manager = ConfigurationManager()
        config = config_manager.get_training_config()
        
        ob = ModelTrainer(config)
        model_training_artifact = ob.initiate_model_trainer(run_name=run_name, exp_id=experiment_id, exp_name=experiment_name)
        model_exp_name = f"{experiment_name}_model_training"
        experiment_id = mlflow.create_experiment(model_exp_name)
        with mlflow.start_run(experiment_id=experiment_id):
            mlflow.log_metric("f1_score", float(model_training_artifact.f1_score))
            mlflow.log_metric("accuracy", float(model_training_artifact.precision_score))
            mlflow.log_metric("accuracy", float(model_training_artifact.recall_score))
            mlflow.log_artifact(config.trained_model_path.as_posix())
        
        return ArtifactSerializer.serialize(model_training_artifact)
        
    dvc_version_trained_model = BashOperator(
        task_id="dvc_version_trained_model",
        bash_command=f"""
            cd /opt/airflow

            RAW_DATA_PATH="{{{{ ti.xcom_pull(task_ids='model_train')['trained_model_path'] }}}}"
            COMMIT_MSG="DVC: Versioned trained model"
            
            ./dags/bash/dvc_track_raw_data.sh "$RAW_DATA_PATH" "$COMMIT_MSG"
        """,
    )
        
    @task()
    def model_eval_push(model_training_artifact: dict):
        logger.info("Model evaluation and push task triggered.")
        
        model_training_artifact = ArtifactSerializer.deserialize(model_training_artifact)
        
        config_manager = ConfigurationManager()
        config = config_manager.get_model_evaluation_config()
        
        ob = ModelEvalPush(config)
        ob.initiate_model_eval_push(model_training_artifact)

        logger.info(f"Model training artifact: {model_training_artifact}")
        
        return model_training_artifact
    
    @task()
    def end_pipeline():
        logger.info("No retraining needed. Skipping model training and evaluation.")
        return 
    
    drift_decision = drift_check()
    training_artifact = model_train()
    end_pipe = end_pipeline()
    eval_push = model_eval_push(training_artifact)
    # If drift_check_task returns "model_train", then model_train_task runs
    # If drift_check_task returns "end_pipeline", then no_retrain_needed_task runs
    drift_decision >> [training_artifact, end_pipe]

    
    training_artifact >> dvc_version_trained_model >> eval_push
        
    
drift_model_training()
