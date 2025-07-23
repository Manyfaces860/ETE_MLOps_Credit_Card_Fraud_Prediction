FROM apache/airflow:slim-latest-python3.11


ENV AIRFLOW_HOME=/opt/airflow
WORKDIR $AIRFLOW_HOME

USER root

COPY requirements.txt .

USER airflow
RUN pip install --no-cache-dir -r requirements.txt

RUN pip install apache-airflow-providers-fab
RUN touch /opt/airflow/.project-root

COPY dags/ ./dags/
COPY logs/ ./logs/
COPY scripts/ ./scripts/
COPY entry.sh ./entry.sh
COPY artifacts/ ./artifacts/
COPY src/ ./src/
COPY config/ ./config/
COPY custom_logs/ ./custom_logs/
