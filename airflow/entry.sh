#!/bin/bash
set -euo pipefail


echo "initializing git repository..."

if [ -z "${GIT_EMAIL}" ]; then
  echo "Error: GIT_EMAIL is not set."
  exit 1
fi

if [ -z "${GIT_NAME}" ]; then
  echo "Error: GIT_NAME is not set."
  exit 1
fi

if [ -d '.git' ]; then
  echo "Git repository already initialized."
else
  echo "Git repository not initialized. Initializing Git..."
  git init
  git config --global user.email "$GIT_EMAIL"
  git config --global user.name "$GIT_NAME"
fi

echo "initializing DVC repository..."
if [ -d '.dvc' ]; then
  echo "DVC already initialized."
else
  echo "DVC not initialized. Initializing DVC..."
  dvc init
  dvc remote add -d "$DVC_REMOTE_NAME" "$DVC_S3_BUCKET"
  dvc remote modify --local "$DVC_REMOTE_NAME" access_key_id "$AWS_ACCESS_KEY_ID"
  dvc remote modify --local "$DVC_REMOTE_NAME" secret_access_key "$AWS_SECRET_ACCESS_KEY"
fi

echo "making scripts executable..."
chmod +x /opt/airflow/dags/bash/dvc_track_raw_data.sh
chmod +x /opt/airflow/dags/bash/dvc_load_task.sh

echo "Starting Airflow Scheduler..."

airflow standalone

echo "Starting Airflow API server..."


echo "Airflow Webserver and Scheduler are running in the background."
echo "Keeping container alive and monitoring background processes..."
