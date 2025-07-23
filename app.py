from fastapi import FastAPI, Request
from src.entity.prediction_input import DataForm
from src.cloud_storage.s3_storage import S3Storage
from src.configuration.config_manager import ConfigurationManager
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from uvicorn import run as app_run
from prometheus_fastapi_instrumentator import Instrumentator
import os
import joblib
import pandas as pd
import sys, pathlib

sys.path.append(pathlib.Path(__file__).parent.absolute().as_posix())


app = FastAPI()
Instrumentator().instrument(app).expose(app)

templates = Jinja2Templates(directory='template')

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", tags=["authentication"])
def index(request: Request):
    
    store = S3Storage()
    config = ConfigurationManager().get_prediction_config()
    
    S3_BUCKET_NAME = config.s3_bucket_name
    S3_FOLDER = config.s3_artifact_dir

    MODEL_FILE_NAME = config.s3_model_name
    PREPROCESSOR_FILE_NAME = config.s3_preprocessor_name
    download_location = config.download_location
    
    print("\n--- Downloading Artifacts ---")
    if not pathlib.Path(os.path.join(download_location, MODEL_FILE_NAME)).exists():
        model_path = store.download_artifact(
            bucket_name=S3_BUCKET_NAME,
            folder_path=S3_FOLDER,
            file_name=MODEL_FILE_NAME,
            serializer='joblib',
            download_location=os.path.join(download_location, MODEL_FILE_NAME)
        )

    if not pathlib.Path(os.path.join(download_location, PREPROCESSOR_FILE_NAME)).exists():
        pre_path = store.download_artifact(
            bucket_name=S3_BUCKET_NAME,
            folder_path=S3_FOLDER,
            file_name=PREPROCESSOR_FILE_NAME,
            serializer='joblib',
            download_location=os.path.join(download_location, PREPROCESSOR_FILE_NAME)
        )

    return templates.TemplateResponse(
            "form.html",{"request": request, "context": "Rendering"})
    
@app.post("/")
async def predict(request: Request):
    try:
        form = DataForm(request)
        
        input_df = await form.get_usvisa_input_data_frame()
        config = ConfigurationManager().get_prediction_config()
        
        model = joblib.load(os.path.join(config.download_location, config.s3_model_name))
        preprocessor = joblib.load(os.path.join(config.download_location, config.s3_preprocessor_name))

        X_processed = preprocessor.fit_transform(input_df)
            
        X_processed_df = pd.DataFrame(X_processed, columns=preprocessor.named_steps['date_age_extractor'].features)

        value = model.predict(X_processed_df)[0]
        
        status = None
        if value == 1:
            status = "He is a Frauuuud"
        else:
            status = "You can bounce"

        return templates.TemplateResponse(
            "form.html",
            {"request": request, "context": status},
        )
        
    except Exception as e:
        return {"status": False, "error": f"{e}"}
    
if __name__ == "__main__":
    app_run(app, host="0.0.0.0", port="8000", reload=True)