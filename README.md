# 🚀 Credit Card Fraud Detection Pipeline

A robust end-to-end MLOps project to detect credit card fraud using Apache Airflow for orchestration, Prometheus + Grafana for monitoring, and FastAPI for real-time predictions. This project is containerized using Docker and uses AWS S3 for model artifact storage, DVC for data versioning, and Git for experiment tracking.

---

## 🛠️ Tech Stack

- **MLOps Orchestration**: Apache Airflow  
- **Model Serving**: FastAPI  
- **Monitoring**: Prometheus, Grafana  
- **Data Versioning**: DVC  
- **Cloud Storage**: AWS S3  
- **Modeling**: Scikit-learn  
- **Infrastructure**: Docker, Docker Compose  
- **Git Integration**: Git + GitHub

---

## 📈 Project Overview

The pipeline is structured into **two main DAGs**:

### 1️⃣ ETL DAG (`ETL.py`)
- **Extract**: Load raw fraud transaction data.
- **Track with DVC**: Push extracted raw data to AWS S3 using DVC.
- **Transform**: Feature engineering (e.g., extract age/date-based features).
- **Load**: Save and version preprocessed data and the fitted preprocessor object.

### 2️⃣ Training DAG (`TRAIN.py`)
- **Drift Detection**: Compares incoming data with reference to detect feature drift.
- **Conditional Training**:
  - If **drift is detected**: ❌ Training is **not** triggered.
  - If **no drift detected**: ✅ Model training proceeds.
- **Model Training**: Train fraud detection model.
- **Evaluation & Push**: Evaluate model and push artifacts (model + preprocessor) to S3.

---

## 📊 Monitoring

This project integrates **Prometheus and Grafana**:

- Prometheus scrapes metrics from FastAPI via `/metrics` exposed using `prometheus_fastapi_instrumentator`.
- Grafana displays metrics dashboards via:
  - `datasources.yml` – Prometheus config
  - `dashboards.json` – Predefined dashboard panel for request stats, latency, etc.

---

## 🌐 Application Behavior

### `app.py` (FastAPI Server)
- On startup:
  - Downloads model and preprocessor from S3 (if not already present).
- On POST request from web UI:
  - Preprocesses user input using the pipeline.
  - Makes predictions using the trained model.
  - Renders prediction result in a form using `Jinja2Templates`.

---

## 🗂️ Project Structure

``` text
.
├── .dvc
├── airflow
│   ├── __init__.py
│   ├── airflow.cfg
│   ├── config
│   ├── dags
│   │   ├── bash
│   │   │   ├── dvc_load_task.sh
│   │   │   └── dvc_track_raw_data.sh
│   │   ├── ETL.py
│   │   └── TRAIN.py
│   ├── Dockerfile
│   ├── entry.sh
│   ├── plugins
│   ├── requirements.txt
│   └── scripts
│       ├── __init__.py
│       ├── data_extract.py
│       ├── data_transform.py
│       ├── drift_detect.py
│       ├── model_evalpush.py
│       └── model_trainer.py
├── app.py
├── artifacts
│   ├── data_ingestion
│   │   ├── fraud_data.csv
│   │   ├── fraud_data.csv.dvc
│   │   └── fraud_data.zip
│   ├── data_transformation
│   │   ├── preprocessing_object
│   │   │   ├── preprocessor.jbl
│   │   │   └── preprocessor.jbl.dvc
│   │   └── transformed
│   │       ├── transformed_data.csv
│   │       └── transformed_data.csv.dvc
│   ├── drift_report
│   │   └── report.yml
│   └── model_training
│       ├── model.jbl
│       └── model.jbl.dvc
├── config
│   ├── config.yml
│   ├── dashboards.yml
│   ├── datasources.yml
│   └── prometheus.yml
├── dashboards
│   └── grafana_dash.json
├── deploy
│   ├── model.jbl
│   └── preprocessor.jbl
├── docker-compose.yml
├── Dockerfile
├── example.env
├── notebooks
│   └── credit_card_fraud_ML_project
│       ├── data
│       │   ├── fraud_data.csv
│       │   └── fraud_data.csv.zip
│       └── notebook
│           ├── explore.ipynb
│           └── file.py
├── pyproject.toml
├── README.md
├── requirements.txt
├── src
│   ├── __init__.py
│   ├── cloud_storage
│   │   ├── __init__.py
│   │   └── s3_storage.py
│   ├── configuration
│   │   ├── __init__.py
│   │   └── config_manager.py
│   ├── constants
│   │   └── __init__.py
│   ├── entity
│   │   ├── __init__.py
│   │   ├── artifact_entity.py
│   │   ├── config_entity.py
│   │   └── prediction_input.py
│   ├── feature_transform
│   │   └── date_age.py
│   ├── logger
│   │   └── __init__.py
│   └── utils
│       ├── __init__.py
│       ├── artifact_serializer.py
│       └── common.py
├── template
│   └── form.html
├── testing.py
└── uv.lock

```
---

## ⚙️ How to Run Locally

```bash
# Clone the repo
git clone https://github.com/your-username/credit-card-fraud-mlops.git
cd credit-card-fraud-mlops

# set env.example variables
# Spin up everything
docker compose up --build -d

# Access Airflow: http://localhost:8080
# Access FastAPI: http://localhost:8000
# Access Grafana: http://localhost:3000
```# ETE_MLOps_Credit_Card_Fraud_Prediction
