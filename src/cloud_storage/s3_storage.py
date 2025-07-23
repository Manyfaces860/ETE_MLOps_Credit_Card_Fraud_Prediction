import boto3
import os
import logging
import joblib # Recommended for scikit-learn models/preprocessors
import pickle # Alternative for general Python objects if joblib isn't suitable
from botocore.exceptions import NoCredentialsError, ClientError
from typing import Any, Optional
from src.logger import logging as logger   
import io



class S3Storage:
    """
    Manages uploading and retrieving machine learning model and preprocessor
    objects to/from an S3 bucket. AWS credentials and region are read from
    environment variables (AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_DEFAULT_REGION).
    """

    def __init__(self):
        """
        Initializes the S3 client.
        Expects AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, and AWS_DEFAULT_REGION
        to be set as environment variables, or configured via AWS CLI/IAM roles.
        """
        try:
            self.s3_client = boto3.client('s3')

            logger.info("S3 client initialized successfully.")
        except NoCredentialsError:
            logger.error("AWS credentials not found. Please set AWS_ACCESS_KEY_ID, "
                         "AWS_SECRET_ACCESS_KEY, and AWS_DEFAULT_REGION environment variables, "
                         "or configure AWS CLI/IAM roles.")
            raise
        except Exception as e:
            logger.error(f"Failed to initialize S3 client: {e}")
            raise

    def _get_s3_object_key(self, folder_path: str, file_name: str) -> str:
        """Helper to construct the full S3 object key."""
        if folder_path and not folder_path.endswith('/'):
            folder_path += '/'
        return f"{folder_path}{file_name}"

    def upload_artifact(
        self,
        obj: Any,
        bucket_name: str,
        folder_path: str,
        file_name: str,
        serializer: str = 'joblib'
    ) -> bool:
        """
        Uploads a Python object (model or preprocessor) to a specified folder in an S3 bucket.

        Args:
            obj (Any): The Python object to upload.
            bucket_name (str): The name of the S3 bucket.
            folder_path (str): The path to the folder within the bucket (e.g., "models/").
            file_name (str): The name of the file to save (e.g., "model.pkl").
            serializer (str): The serialization method ('joblib' or 'pickle'). Defaults to 'joblib'.

        Returns:
            bool: True if the upload was successful, False otherwise.
        """
        s3_object_key = self._get_s3_object_key(folder_path, file_name)
        logger.info(f"Attempting to upload '{file_name}' to s3://{bucket_name}/{s3_object_key}")

        try:
            buffer = io.BytesIO()
            joblib.dump(obj, buffer)
            self.s3_client.put_object(Bucket=bucket_name, Key=s3_object_key, Body=buffer.getvalue())
            logger.info(f"Successfully uploaded '{file_name}' to s3://{bucket_name}/{s3_object_key}")
            return True
        except ClientError as e:
            logger.error(f"S3 ClientError during upload: {e}")
            return False
        except Exception as e:
            logger.error(f"An unexpected error occurred during upload: {e}")
            return False

    def download_artifact(
        self,
        bucket_name: str,
        folder_path: str,
        file_name: str,
        download_location: str,
        serializer: str = 'joblib'
    ) -> Optional[Any]:
        """
        Downloads and deserializes a Python object from a specified folder in an S3 bucket.

        Args:
            bucket_name (str): The name of the S3 bucket.
            folder_path (str): The path to the folder within the bucket (e.g., "models/").
            file_name (str): The name of the file to download (e.g., "model.pkl").
            serializer (str): The deserialization method ('joblib' or 'pickle'). Defaults to 'joblib'.

        Returns:
            Any: The deserialized Python object, or None if download/deserialization failed.
        """
        s3_object_key = self._get_s3_object_key(folder_path, file_name)
        logger.info(f"Attempting to download '{file_name}' from s3://{bucket_name}/{s3_object_key}")

        try:
            response = self.s3_client.get_object(Bucket=bucket_name, Key=s3_object_key)
            downloaded_bytes = response['Body'].read()
            # Create a new BytesIO buffer from bytes
            buffer_from_bytes = io.BytesIO(downloaded_bytes)
            logger.info(f"Successfully downloaded '{file_name}'.")
            print("*"*40 , f"trying to load {file_name}")
            try: 
                loaded_object = joblib.load(buffer_from_bytes)
            except Exception as e:
                print(e, "exception happend hhhhhh")
            print("*"*40 , loaded_object, f"this should be the loaded object {file_name}")
            
            logger.info(f"Successfully deserialized '{file_name}'.")
            
            joblib.dump(loaded_object, download_location)
            
            return download_location
        except ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchKey':
                logger.error(f"Object not found: s3://{bucket_name}/{s3_object_key}")
            else:
                logger.error(f"S3 ClientError during download: {e}")
            return None
        except Exception as e:
            logger.error(f"An unexpected error occurred during download/deserialization: {e}")
            return None

