# 🚀 Credit Card Fraud Detection MLOps Pipeline

A robust end-to-end MLOps project to detect credit card fraud using Apache Airflow for orchestration, Prometheus + Grafana for monitoring, and FastAPI for real-time predictions. This project is containerized using Docker and uses AWS S3 for model artifact storage, DVC for data versioning, and Git for experiment tracking. It is deployed on AWS EC2 using Docker Compose, with container images stored on Amazon ECR and CI/CD managed by GitHub Actions.

---

## 🛠️ Tech Stack

* **MLOps Orchestration**: Apache Airflow
* **Model Serving**: FastAPI
* **Monitoring**: Prometheus, Grafana
* **Data Versioning**: DVC
* **Cloud Storage**: AWS S3
* **Modeling**: Scikit-learn
* **Experiment Tracking**: MLflow via DagsHub
* **Image Registry**: Amazon ECR
* **Infrastructure**: Docker, Docker Compose
* **CI/CD**: GitHub Actions
* **Cloud Compute**: AWS EC2

---

## 📊 Project Overview

The pipeline is structured into **two main DAGs**:

### 1️⃣ ETL DAG (`ETL.py`)

* **Extract**: Load raw fraud transaction data.
* **Track with DVC**: Push extracted raw data to AWS S3 using DVC.
* **Transform**: Feature engineering (e.g., extract age/date-based features).
* **Load**: Save and version preprocessed data and the fitted preprocessor object.

### 2️⃣ Training DAG (`TRAIN.py`)

* **Drift Detection**: Compares incoming data with reference to detect feature drift.
* **Conditional Training**:

  * If **drift is detected**: ❌ Training is **not** triggered.
  * If **no drift detected**: ✅ Model training proceeds.
* **Model Training**: Train fraud detection model.
* **Evaluation & Push**: Evaluate model and push artifacts (model + preprocessor) to S3.

---

## 📊 Monitoring

This project integrates **Prometheus and Grafana**:

* Prometheus scrapes metrics from FastAPI via `/metrics` exposed using `prometheus_fastapi_instrumentator`.
* Grafana displays metrics dashboards via:

  * `datasources.yml` – Prometheus config
  * `grafana_dash.json` – Predefined dashboard panel for request stats, latency, etc.

---

## 🌐 Application Behavior

### `app.py` (FastAPI Server)

* On startup:

  * Downloads model and preprocessor from S3 (if not already present).

* On POST request from web UI:

  * Preprocesses user input using the pipeline.
  * Makes predictions using the trained model.
  * Renders prediction result in a form using `Jinja2Templates`.

---

## 📂 Project Structure

```text
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

## 🔄 Experiment Tracking with MLflow (via DagsHub)

This project uses **DagsHub integrated with MLflow** to track and visualize experiments:

* MLflow logs are automatically pushed to DagsHub's MLflow dashboard.
* Each training run logs:

  * Parameters
  * Metrics
  * Artifacts (model, preprocessor)


> View Experiments on DagsHub: `https://dagshub.com/<your-username>/<your-repo>/experiments`

---

## 🚢 Deployment Overview

The system is fully production-ready and runs on AWS EC2.

### 🏐 GitHub Actions (CI/CD)

* Triggered on push to `main`
* Builds Docker images for all services (Airflow, FastAPI, etc.)
* Pushes them to **Amazon ECR**
* SSH into EC2 to pull and restart containers using `docker-compose`

### 📁 Amazon ECR

Stores Docker images for:

* Airflow
* FastAPI
* Prometheus
* Grafana

### 🌎 AWS EC2

Runs the full MLOps stack using `docker-compose` with port exposure for:

* Airflow: `http://<ec2-ip>:8080`
* FastAPI: `http://<ec2-ip>:8000`
* Grafana: `http://<ec2-ip>:3000`

---

## 🚲 Deployment Architecture

```
+-------------+       Push to main       +---------------------+
| Developer   |  --------------------->  | GitHub Actions CI/CD|
+-------------+                          +---------------------+
                                                  |
                                                  | Builds Docker image
                                                  v
                                        +----------------------+
                                        | Amazon ECR (Docker)  |
                                        +----------------------+
                                                  |
                                                  | SSH + Pull + Restart
                                                  v
                                     +-----------------------------+
                                     | AWS EC2                     |
                                     |   docker-compose up         |
                                     +-----------------------------+
                                                  |
             +-------------+----------+------------+-------------+
             |             |          |            |             |
        Airflow       FastAPI     Prometheus    Grafana      MLflow UI (DagsHub)
      (port 8080)    (port 8000)   (port 9090)   (port 3000)   (via web link)
```

---

## ⚙️ Run Locally

```bash
# Clone the repo
git clone https://github.com/Manyfaces860/ETE_MLOps_Credit_Card_Fraud_Prediction.git
cd ETE_MLOps_Credit_Card_Fraud_Prediction

# Set environment variables in .env
cp example.env .env

# Spin up everything
# set AIRFLOW_UID and give necessary permissions to airflow for successfully running airflow container
docker compose up --build -d

# Access UIs
# Airflow:   http://localhost:8080
# FastAPI:   http://localhost:8000
# Grafana:   http://localhost:3000
```

---

## 🛡️ Secrets Required (GitHub Actions)

`AWS_ACCESS_KEY_ID`  
`AWS_SECRET_ACCESS_KEY`
`AIRFLOW_UID`
`GIT_EMAIL`
`GIT_NAME`
`DVC_REMOTE_NAME`
`DVC_S3_BUCKET`
`AWS_DEFAULT_REGION`

---
