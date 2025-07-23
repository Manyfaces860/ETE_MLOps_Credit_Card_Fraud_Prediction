from dataclasses import dataclass


@dataclass
class DataIngestionArtifact:
    data_ingestion_unzip_file_path: str
    status: bool
        
@dataclass
class DataTransformationArtifact:
    transformed_object_file_path:str 
    transformed_file_path:str
    status: bool

@dataclass
class ModelTrainingArtifact:
    trained_model_path:str
    f1_score:float
    precision_score:float
    recall_score:float    
