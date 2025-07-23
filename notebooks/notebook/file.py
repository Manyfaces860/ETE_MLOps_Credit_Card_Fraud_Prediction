import pandas as pd
import numpy as np
import warnings
from sklearn.model_selection import train_test_split
from sklearn.utils import resample
from sklearn.preprocessing import MinMaxScaler, StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score

warnings.filterwarnings("ignore")

df = pd.DataFrame(pd.read_csv("../data/fraud_data.csv"))
df['trans_date_trans_time'] = pd.to_datetime(df['trans_date_trans_time'], format="mixed")
df['dob'] = pd.to_datetime(df['dob'], format="mixed")
df['age'] = df['trans_date_trans_time'].dt.year - df['dob'].dt.year
df['is_fraud'] = df['is_fraud'].apply(lambda x: int(str(x).split('"')[0]))

x=df[['amt','age','city_pop','merch_long']]
y=df['is_fraud']

# Separate majority and minority classes
df_majority = df[df['is_fraud'] == 0]
df_minority = df[df['is_fraud'] == 1]

# Upsample minority class
df_minority_upsampled = resample(df_minority, 
                                 replace=True,     # Sample with replacement
                                 n_samples=len(df_majority),    # Match number in majority class
                                 random_state=123) # Reproducible results

# Combine majority class with upsampled minority class
df_upsampled = pd.concat([df_majority, df_minority_upsampled])

# Display new class counts
print(df_upsampled['is_fraud'].value_counts())

x=MinMaxScaler().fit_transform(x)

x_train, x_test, y_train, y_test = train_test_split(x,y,random_state=42,test_size=0.2)
rf = RandomForestClassifier(max_depth=1200,n_estimators=120,random_state=42)
rf.fit(x_train,y_train)
y_pred = rf.predict(x_test)
print("accuracy score: ", accuracy_score(y_pred,y_test))

