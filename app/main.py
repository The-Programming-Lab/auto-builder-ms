from dotenv import load_dotenv
load_dotenv()
from fastapi import FastAPI
import os

from app.api.v1.router import router
from app.core.logging import logger
from app.utils.utility import run_command

if os.getenv("BASE_PATH") is None:
    os.environ["BASE_PATH"] = ""
    logger.critical("BASE_PATH is not set, setting to empty string")

BASE_PATH = os.getenv("BASE_PATH")
GOOGLE_KEY_PATH = os.getenv("GOOGLE_KEY_PATH")
CLUSTER_ZONE = os.getenv("CLUSTER_ZONE")
PROJECT_ID = os.getenv("PROJECT_ID")

app = FastAPI(docs_url=BASE_PATH + "/docs", openapi_url=BASE_PATH + "/openapi.json") # type: ignore

# auth gcloud and get cluster
run_command(f'gcloud auth activate-service-account --key-file={GOOGLE_KEY_PATH}')
# devnull needed to hide the output as gcp would log it as error
with open(os.devnull, 'w') as devnull:
    run_command(f'gcloud container clusters get-credentials main --zone={CLUSTER_ZONE} --project={PROJECT_ID}', stdout=devnull)
logger.info(f"Got cluster zone: {CLUSTER_ZONE}, project: {PROJECT_ID}, cluster: main")

app.include_router(router)


@app.get("/")
async def health_check():
    return "ok"