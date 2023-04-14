from fastapi import FastAPI
from app.api.v1.router import router
import subprocess
from app.core.config import GCP_AUTH_FILE


app = FastAPI()

# auth gcloud and get cluster
try:
    subprocess.check_call(f'gcloud auth activate-service-account --key-file={GCP_AUTH_FILE}', shell=True)
except Exception as e:
    print(e)

# !!! This is the way to disable docs and openapi.json in production !!!
# app = FastAPI(docs_url=None if env == "production" else "/docs",
#               redoc_url=None,
#               openapi_url=None if env == "production" else "/openapi.json")


# add router from api/endpoints/example.py
app.include_router(router)