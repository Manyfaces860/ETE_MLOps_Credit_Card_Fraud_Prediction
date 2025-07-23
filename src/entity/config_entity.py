from dataclasses import dataclass
from pathlib import Path
 
@dataclass(frozen=True)
class DataIngestionConfig:
  dir_name: Path
  source_URL: str
  zip_file_name: Path
  unzip_dir: Path
    
@dataclass
class DataTransformationConfig:
  dir_name: Path
  transformed_data_dir: Path
  preprocess_pipeline_object_dir: Path
  transformed_data_file_name: str
  preprocess_pipeline_object_file_name: str
                           
@dataclass
class DataDriftConfig:
  dir_name: Path
  file_name: str
  refrence_data_path: Path
  transformed_data_path: Path
  mlflow_uri: str
                                                    
@dataclass
class ModelTrainingConfig:
  dir_name: Path
  training_data_path: Path
  trained_model_path: Path
  train_test_ratio: float
  mlflow_uri: str
  target_column: str
    
@dataclass
class ModelEvaluationConfig:
  expected_score: float
  preprocessor_object_path: str
  s3_bucket_name: str
  s3_model_name: str
  s3_artifact_dir: str
  s3_preprocessor_name: str

@dataclass
class PredictionConfig:
  s3_bucket_name: str
  s3_model_name: str
  s3_artifact_dir: str
  s3_preprocessor_name: str
  download_location: str


# @dataclass
# class ModelPusherConfig:
#     bucket_name: str = MODEL_BUCKET_NAME
#     s3_model_key_path: str = MODEL_NAME




# @dataclass
# class USvisaPredictorConfig:
#     model_file_path: str = MODEL_NAME
#     model_bucket_name: str = MODEL_BUCKET_NAME