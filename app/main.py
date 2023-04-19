from fastapi import FastAPI
import subprocess
import os

from app.api.v1.router import router
from app.core.config import GCP_AUTH_FILE, BASE_PATH, CLUSTER_ZONE, PROJECT_ID
from app.core.logging import logger
from app.utils.utility import run_command



app = FastAPI(docs_url=BASE_PATH + "/docs", openapi_url=BASE_PATH + "/openapi.json")

# auth gcloud and get cluster
run_command(f'gcloud auth activate-service-account --key-file={GCP_AUTH_FILE}')
# devnull needed to hide the output as gcp would log it as error
with open(os.devnull, 'w') as devnull:
    run_command(f'gcloud container clusters get-credentials main --zone={CLUSTER_ZONE} --project={PROJECT_ID}', stdout=devnull)
logger.info(f"Got cluster zone: {CLUSTER_ZONE}, project: {PROJECT_ID}, cluster: main")

app.include_router(router)


@app.get("/")
async def health_check():
    return "ok"