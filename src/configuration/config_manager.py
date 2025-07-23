import os
from src.constants import *
from src.utils.common import read_yaml, create_directories
from src.entity.config_entity import (DataIngestionConfig, DataTransformationConfig,
                                                       ModelTrainingConfig,
                                                       DataDriftConfig,
                                                       ModelEvaluationConfig,
                                                       PredictionConfig
                                                       )
                                                


class ConfigurationManager:
    def __init__(self):
        self.config = read_yaml(CONFIG_FILE_PATH)
        create_directories([self.config.artifacts_root])
        
    def get_data_ingestion_config(self) -> DataIngestionConfig:
        config = self.config.data_ingestion

        create_directories([config.dir_name])

        data_ingestion_config = DataIngestionConfig(
            dir_name=Path(config.dir_name),
            source_URL=config.source_URL,
            zip_file_name=config.zip_file_name,
            unzip_dir=Path(config.unzip_dir) 
        )

        return data_ingestion_config
    
    def get_data_transformation_config(self) -> DataTransformationConfig:
        config = self.config.data_transformation
        
        create_directories([config.dir_name])
        
        data_transformation_config = DataTransformationConfig(
            dir_name=Path(config.dir_name),
            transformed_data_dir=Path(config.transformed_data_dir),
            preprocess_pipeline_object_dir=Path(config.preprocess_pipeline_object_dir),
            transformed_data_file_name=config.transformed_data_file_name,
            preprocess_pipeline_object_file_name=config.preprocess_pipeline_object_file_name
        )
    
        return data_transformation_config

    def get_training_config(self) -> ModelTrainingConfig:
        config = self.config.model_training
        
        create_directories([config.dir_name])
        
        model_training_config = ModelTrainingConfig(
            dir_name = Path(config.dir_name),
            training_data_path = Path(config.training_data_path),
            trained_model_path = Path(config.trained_model_path),
            train_test_ratio = config.train_test_ratio,
            mlflow_uri = config.mlflow_uri,
            target_column = config.target_column
        )
        
        return model_training_config
    
    def get_data_drift_config(self):
        config = self.config.data_drift
        
        create_directories([config.dir_name])
        
        data_drift_config = DataDriftConfig(
            dir_name=Path(config.dir_name),
            file_name=Path(config.file_name),
            refrence_data_path=Path(config.refrence_data_path),
            transformed_data_path=Path(config.transformed_data_path),
            mlflow_uri=config.mlflow_uri
        )
        
        return data_drift_config
    
    def get_model_evaluation_config(self) -> ModelEvaluationConfig:
        
        config = self.config.model_eval_push
        
        model_evaluation_config = ModelEvaluationConfig(
            expected_score=config.expected_score,
            preprocessor_object_path=config.preprocessor_object_path,
            s3_bucket_name=config.s3_bucket_name,
            s3_model_name=config.s3_model_name,
            s3_artifact_dir=config.s3_artifact_dir,
            s3_preprocessor_name=config.s3_preprocessor_name
        )
        
        return model_evaluation_config
    
    def get_prediction_config(self) -> PredictionConfig:
        
        config = self.config.prediction
        
        prediction_config = PredictionConfig(
            s3_bucket_name=config.s3_bucket_name,
            s3_model_name=config.s3_model_name,
            s3_artifact_dir=config.s3_artifact_dir,
            s3_preprocessor_name=config.s3_preprocessor_name,
            download_location=config.download_location
        )
        
        return prediction_config
    
    
