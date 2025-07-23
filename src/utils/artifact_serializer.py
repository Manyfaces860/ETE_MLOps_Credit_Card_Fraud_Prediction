from src.entity.artifact_entity import DataIngestionArtifact, DataTransformationArtifact, ModelTrainingArtifact
from logger import logging as logger

class ArtifactSerializer:
    @staticmethod
    def serialize(obj):
        logger.info(f"Serializing DataIngestionArtifact: {obj}")
        # --- VERY IMPORTANT DEBUGGING LINES ---
        # logger.info(f"DEBUG: Type of obj being passed: {type(obj)}")
        # logger.info(f"DEBUG: Type of DataIngestionArtifact in serializer's scope: {DataIngestionArtifact}")
        # logger.info(f"DEBUG: Are they the EXACT SAME object? {type(obj) is DataIngestionArtifact}")
        # --- END DEBUGGING LINES ---
        if isinstance(obj, DataIngestionArtifact):
            return {
                "__class__": "DataIngestionArtifact",
                "data_ingestion_unzip_file_path": obj.data_ingestion_unzip_file_path,
                "status": obj.status,
            }
        elif isinstance(obj, DataTransformationArtifact):
            return {
                "__class__": "DataTransformationArtifact",
                "transformed_object_file_path": obj.transformed_object_file_path,
                "transformed_file_path": obj.transformed_file_path,
                "status": obj.status,
            }
        elif isinstance(obj, ModelTrainingArtifact):
            return {
                "__class__": "ModelTrainingArtifact",
                "trained_model_path": obj.trained_model_path,
                "f1_score": obj.f1_score,
                "recall_score": obj.recall_score,
                "precision_score": obj.precision_score,
            }
        else:
            raise TypeError(f"Object of type {obj.__class__.__name__} is not serializable by ArtifactSerializer")

    @staticmethod
    def deserialize(data: dict):
        logger.info(f"Deserializing data: {data}")
        if not isinstance(data, dict) or "__class__" not in data:
            raise ValueError("Invalid data format for deserialization: missing '__class__' key")

        class_name = data["__class__"]

        if class_name == "DataIngestionArtifact":
            return DataIngestionArtifact(
                data_ingestion_unzip_file_path=data["data_ingestion_unzip_file_path"],
                status=data["status"],
            )
        elif class_name == "DataTransformationArtifact":
            return DataTransformationArtifact(
                transformed_object_file_path=data["transformed_object_file_path"],
                transformed_file_path=data["transformed_file_path"],
                status=data["status"],
            )
        elif class_name == "ModelTrainingArtifact":
            return ModelTrainingArtifact(
                trained_model_path=data["trained_model_path"],
                f1_score=data["f1_score"],
                precision_score= data["precision_score"],
                recall_score= data["recall_score"],
            )
        else:
            raise ValueError(f"Unknown class name for deserialization: {class_name}")