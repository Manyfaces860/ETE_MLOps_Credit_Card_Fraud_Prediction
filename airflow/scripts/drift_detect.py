from evidently import Report
from evidently.presets import DataDriftPreset 
import pandas as pd
from src.logger import logging as logger
import datetime, os
from src.entity.config_entity import DataDriftConfig

class DataDrift:
    def __init__(self, config: DataDriftConfig, run_name: str, experiment_name: str):
        self.config = config
        self.run_name = run_name
        self.experiment_name = experiment_name
    
    def detect_dataset_drift(self):
        OVERALL_DRIFT_SHARE_THRESHOLD = 0.2
        
        try:
            data = pd.read_csv(self.config.transformed_data_path)
            reference_df, current_df = data, data
            
            report = Report([
                DataDriftPreset() 
            ])

            my_eval = report.run(reference_df, current_df)

            drift_detected = False
            drift_share_value = 0.0 # Default value
            
            try:
                report_data = my_eval.dict()

                # Find the DriftedColumnsCount metric
                for metric in report_data.get('metrics', []):
                    if metric.get('metric_id') == 'DriftedColumnsCount(drift_share=0.5)': # Match the exact metric_id
                        drift_share_value = float(metric['value']['share']) # Extract the 'share' value
                        break # Found the metric, no need to continue loop

                logger.info(f"Detected drifted columns share: {drift_share_value}")

                if drift_share_value <= OVERALL_DRIFT_SHARE_THRESHOLD:
                    logger.warning(f"Overall drift share ({drift_share_value:.2%}) exceeds threshold ({OVERALL_DRIFT_SHARE_THRESHOLD:.2%}). Triggering retraining.")
                    drift_detected = True
                else:
                    logger.info(f"Overall drift share ({drift_share_value:.2%}) is below threshold. No retraining needed.")

                my_eval.save_html(os.path.join(self.config.dir_name, self.config.file_name))
                
                

            except Exception as e:
                logger.error(f"Error processing drift report: {e}")
                raise Exception(f"Error processing drift report: {e}")

            if drift_detected:
                logger.info("Drift detected, retraining model.")
                return "model_train", os.path.join(self.config.dir_name, self.config.file_name)
            else:
                logger.info("No drift detected, no retraining needed.")
                return "end_pipeline", os.path.join(self.config.dir_name, self.config.file_name)
            
        except Exception as e:
            logger.error(f"Error in detecting dataset drift: {e}")
            raise Exception(f"Error in detecting dataset drift: {e}")
            
    
