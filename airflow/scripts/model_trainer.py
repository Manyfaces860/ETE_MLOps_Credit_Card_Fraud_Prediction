import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score
import joblib
from src.logger import logging
from src.entity.config_entity import ModelTrainingConfig
from src.entity.artifact_entity import ModelTrainingArtifact


class ModelTrainer:
    def __init__(self, config: ModelTrainingConfig):
        """
        :param data_ingestion_artifact: Output reference of data ingestion artifact stage
        :param data_transformation_config: Configuration for data transformation
        """

        self.config = config
        
    def train(self):
        """
        Method Name :   get_model_object_and_report
        Description :   This function uses neuro_mf to get the best model object and report of the best model
        
        Output      :   Returns metric artifact object and best model object
        On Failure  :   Write an exception log and then raise an exception
        """
        try:
            logging.info("Training triggered ")
            
            df = pd.read_csv(self.config.training_data_path)
            x_train, x_test, y_train, y_test = train_test_split(
                df.drop(columns=[self.config.target_column]),
                df[self.config.target_column],
                test_size=self.config.train_test_ratio,
                random_state=42
            )
            
            model = RandomForestClassifier(max_depth=1200,n_estimators=120,random_state=42)
            model.fit(x_train,y_train)
            
            y_pred = model.predict(x_test)

            accuracy = accuracy_score(y_test, y_pred) 
            f1 = f1_score(y_test, y_pred)  
            precision = precision_score(y_test, y_pred)  
            recall = recall_score(y_test, y_pred)
            
            return model, accuracy, f1, precision, recall
        
        except Exception as e:
            logging.error(f"Error in get_model_object_and_report: {e}")
            raise Exception(f"Error in get_model_object_and_report: {e}")
            

    def initiate_model_trainer(self, run_name: str, exp_id: str, exp_name: str) -> ModelTrainingArtifact:
        logging.info("Entered initiate_model_trainer method of ModelTrainer class")
        """
        Method Name :   initiate_model_trainer
        Description :   This function initiates a model trainer steps
        
        Output      :   Returns model trainer artifact
        On Failure  :   Write an exception log and then raise an exception
        """
        try:
            logging.info("Initiating model trainer process")
            model, accuracy, f1, precision, recall = self.train()
            logging.info(f"Model training completed with accuracy: {accuracy}, f1: {f1}, precision: {precision}, recall: {recall}")

            joblib.dump(model, self.config.trained_model_path)

            model_trainer_artifact = ModelTrainingArtifact(
                trained_model_path=self.config.trained_model_path.as_posix(),
                f1_score=f1,
                precision_score=precision,
                recall_score=recall
            )
            
            
            logging.info(f"Model trainer artifact: {model_trainer_artifact}")
            return model_trainer_artifact
        except Exception as e:
            logging.error(f"Error in initiate_model_trainer: {e}")
            raise Exception(f"Error in initiate_model_trainer: {e}")