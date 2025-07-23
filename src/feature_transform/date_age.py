from sklearn.base import BaseEstimator, TransformerMixin
import pandas as pd


class DateAgeFeatureExtractor(BaseEstimator, TransformerMixin):
    """
    A custom transformer to:
    1. Convert 'trans_date_trans_time' and 'dob' to datetime objects.
    2. Calculate 'age' from these datetime columns.
    3. Select the specified features for the pipeline.
    """
    def __init__(self, features=['amt', 'age', 'city_pop', 'merch_long']):
        self.features = features

    def fit(self, X, y=None):
        return self # Nothing to learn from data

    def transform(self, X):
        # Ensure we are working on a copy to avoid modifying the original DataFrame
        X_transformed = X.copy()

        # Convert date columns to datetime, handling mixed formats
        X_transformed['trans_date_trans_time'] = pd.to_datetime(X_transformed['trans_date_trans_time'], format="mixed", errors='coerce')
        X_transformed['dob'] = pd.to_datetime(X_transformed['dob'], format="mixed", errors='coerce')

        # Calculate age
        # Handle potential NaT values from 'errors='coerce' in to_datetime
        X_transformed['age'] = X_transformed['trans_date_trans_time'].dt.year - X_transformed['dob'].dt.year
        
        return X_transformed[self.features]