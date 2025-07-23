import os, sys
# sys.path.append(os.path.abspath(os.path.join(os.path.join(os.path.dirname(__file__), '..'), '..')))

import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.utils import resample
from src.logger import logging as logger
from src.entity.config_entity import DataTransformationConfig
from src.entity.artifact_entity import DataTransformationArtifact
from src.entity.artifact_entity import DataIngestionArtifact
from src.utils.common import create_directories
import joblib
from typing import Tuple
from src.feature_transform.date_age import DateAgeFeatureExtractor


class DataTransformation:
    
    def __init__(self, config: DataTransformationConfig):
        self.config = config
        self.pipeline = Pipeline(steps=[
            ('date_age_extractor', DateAgeFeatureExtractor()),
            ('scaler', StandardScaler())
        ])
        
        
    def transform_data(self, artifact: DataIngestionArtifact) -> DataTransformationArtifact:
        try : 
            df = pd.read_csv(artifact.data_ingestion_unzip_file_path)
            
            df['is_fraud'] = df['is_fraud'].apply(lambda x: int(str(x).split('"')[0]))
            
            x_upsampled, y_upsampled = self.resample_data(df)
            logger.info(f"Resampled data shapes: X - {x_upsampled.shape}, y - {y_upsampled.shape}")
            X_processed = self.pipeline.fit_transform(x_upsampled, y_upsampled)
            
            X_processed_df = pd.DataFrame(X_processed, columns=self.pipeline.named_steps['date_age_extractor'].features)
            y_upsampled_reset_index = y_upsampled.reset_index(drop=True)

            # It's good practice to rename the Series to be its column name before concat
            y_upsampled_reset_index.name = 'is_fraud'

            # 4. Concatenate X_processed_df and y_upsampled_reset_index
            # Use axis=1 to concatenate them side-by-side (as columns)
            final_processed_df = pd.concat([X_processed_df, y_upsampled_reset_index], axis=1)

            # 5. Save the combined DataFrame to a CSV file
            create_directories([self.config.transformed_data_dir, self.config.preprocess_pipeline_object_dir])
            
            output_filename = os.path.join(self.config.transformed_data_dir, self.config.transformed_data_file_name)
            object_filename = os.path.join(self.config.preprocess_pipeline_object_dir, self.config.preprocess_pipeline_object_file_name)
            
            final_processed_df.to_csv(output_filename, index=False) # index=False prevents writing the DataFrame index as a column
            joblib.dump(self.pipeline, object_filename)
            
            logger.info(f"\nFinal processed DataFrame created with shape: {final_processed_df.shape}")
            logger.info(f"Columns of the final DataFrame: {final_processed_df.columns.tolist()}")
            logger.info(f"First 5 rows of the final processed DataFrame:\n{final_processed_df.head()}")
            logger.info(f"Pipeline object saved to {object_filename}")
            logger.info(f"Transformed data saved to {output_filename}")            
            
            return DataTransformationArtifact(
                transformed_object_file_path=object_filename,
                transformed_file_path=output_filename,
                status=True
            )
            
        except Exception as e:
            logger.error(f"Error during data transformation: {e}")
            return DataTransformationArtifact(
                transformed_object_file_path=object_filename,
                transformed_file_path=output_filename,
                status=False
            )

        
        

    def resample_data(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Resample the DataFrame to balance the classes.
        """
        X = df.drop(columns=['is_fraud'])
        y = df['is_fraud']

        # --- 6. Apply Resampling (OUTSIDE the Pipeline, on training data) ---
        # For demonstration, we'll simulate a training split.
        # In a real scenario, you'd perform train_test_split first.
        # Here, we're just showing the upsampling logic.

        # Separate majority and minority classes for resampling
        X_majority, X_minority = X[y == 0], X[y == 1]
        y_majority, y_minority = y[y == 0], y[y == 1]

        logger.info(f"Original majority samples: {len(X_majority)}")
        logger.info(f"Original minority samples: {len(X_minority)}")

        # Upsample minority class features and target
        X_minority_upsampled, y_minority_upsampled = resample(
            X_minority, y_minority,
            replace=True,         # Sample with replacement
            n_samples=len(X_majority), # Match number in majority class
            random_state=123      # Reproducible results
        )

        # Combine majority class with upsampled minority class
        X_upsampled = pd.concat([X_majority, X_minority_upsampled])
        y_upsampled = pd.concat([y_majority, y_minority_upsampled])

        logger.info(f"\nUpsampled X shape: {X_upsampled.shape}")
        logger.info(f"Upsampled y value counts:\n{y_upsampled.value_counts()}")
        
        return (X_upsampled, y_upsampled)
    
    
    def initiate_data_transformation(self, artifact: DataIngestionArtifact) -> DataTransformationArtifact:
        """initiate data transformation"""
        
        return self.transform_data(artifact)
        
    
    





