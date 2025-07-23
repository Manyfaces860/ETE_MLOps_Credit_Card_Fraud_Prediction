from src.logger import logging as logger
from src.entity.config_entity import ModelEvaluationConfig
from src.entity.artifact_entity import ModelTrainingArtifact
from src.cloud_storage.s3_storage import S3Storage
import joblib

class ModelEvalPush:
    def __init__(self, config: ModelEvaluationConfig):
        self.config = config
        self.store = S3Storage()

    def model_eval(self, model_trainer_artifact: ModelTrainingArtifact):
        if model_trainer_artifact.f1_score < self.config.expected_score:
            logger.info(f"Model evaluation failed with F1 score: {model_trainer_artifact.f1_score}. Expected score: {self.config.expected_score}.")
            return False   

        return True
                
    def model_push(self, model_path: str):
        model = joblib.load(model_path)
        preprocessor = joblib.load(self.config.preprocessor_object_path)
        
        S3_BUCKET_NAME = self.config.s3_bucket_name
        S3_FOLDER = self.config.s3_artifact_dir

        MODEL_FILE_NAME = self.config.s3_model_name
        PREPROCESSOR_FILE_NAME = self.config.s3_preprocessor_name

        print("\n--- Uploading Artifacts ---")
        upload_model_success = self.store.upload_artifact(
            obj=model,
            bucket_name=S3_BUCKET_NAME,
            folder_path=S3_FOLDER,
            file_name=MODEL_FILE_NAME,
            serializer='joblib'
        )

        upload_preprocessor_success = self.store.upload_artifact(
            obj=preprocessor,
            bucket_name=S3_BUCKET_NAME,
            folder_path=S3_FOLDER,
            file_name=PREPROCESSOR_FILE_NAME,
            serializer='joblib'
        )


    def initiate_model_eval_push(self, model_trainer_artifact):
        try:
            logger.info("Entered initiate_model_eval_push method of ModelEvalPush class")
            # Logic to push the model to S3
            if self.model_eval(model_trainer_artifact):
                logger.info("Model evaluation passed. Proceeding to push the model.")
                self.model_push(model_trainer_artifact.trained_model_path,)

            else:
                logger.info("Model evaluation failed. Not pushing the model.")
            
                        
        except Exception as e:
            logger.error(f"Error in initiate_model_eval_push: {e}")
            raise Exception(f"error in model_eval_push: {e}")