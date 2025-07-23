import os, sys
# sys.path.append(os.path.abspath(os.path.join(os.path.join(os.path.dirname(__file__), '..'), '..')))

import zipfile
import gdown
from src.logger import logging as logger
from src.utils.common import create_directories
from src.entity.config_entity import DataIngestionConfig
from src.entity.artifact_entity import DataIngestionArtifact


class DataIngestion:
    """Data ingestion class to handle downloading and extracting data files.
    """
    def __init__(self, config: DataIngestionConfig):
        self.config = config
        
    def download_file(self):
        try:
            dataset_url = self.config.source_URL
            zip_download_name = os.path.join(self.config.dir_name, self.config.zip_file_name)
            
            logger.info(f"Downloading data from {dataset_url} into file {zip_download_name}")
            
            file_id = dataset_url.split("/")[-2]
            prefix = 'https://drive.google.com/uc?/export=download&id='
            gdown.download(prefix+file_id, zip_download_name)
            
            logger.info(f"Downloaded data from {dataset_url} into file {zip_download_name}")
            
        except Exception as e:
            raise e
        
    def extract_zip_file(self):
        """
        zip_file_path: str
        Extracts the zip file into the data directory
        Function returns None
        """
        
        unzip_path = self.config.unzip_dir
        zip_path = os.path.join(self.config.dir_name, self.config.zip_file_name)
        
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(unzip_path)
            
    def initiate_data_ingestion(self) -> DataIngestionArtifact:
        """
        Method Name :   initiate_data_ingestion
        Description :   This method initiates the data ingestion process by downloading and extracting the data.
        
        Output      :   None
        On Failure  :   Write an exception log and then raise an exception
        """
        logger.info("Starting data ingestion process")
        
        try:
            self.download_file()
            logger.info("Data file downloaded successfully")
            
            self.extract_zip_file()
            logger.info("Data file extracted successfully")
            
            output = os.path.join(self.config.unzip_dir, self.config.zip_file_name.replace('.zip', '.csv'))
            return DataIngestionArtifact(
                data_ingestion_unzip_file_path=output,
                status=True
            )
            
        except Exception as e:
            logger.error(f"Error during data ingestion: {e}")
            
            return DataIngestionArtifact(
                data_ingestion_unzip_file_path=output,
                status=False
            )
            
            