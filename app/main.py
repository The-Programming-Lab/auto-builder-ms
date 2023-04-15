from fastapi import FastAPI
from app.api.v1.router import router
import subprocess
from app.core.config import GCP_AUTH_FILE, BASE_PATH


app = FastAPI(docs_url=BASE_PATH + "/docs", openapi_url=BASE_PATH + "/openapi.json")

# auth gcloud and get cluster
try:
    subprocess.check_call(f'gcloud auth activate-service-account --key-file={GCP_AUTH_FILE}', shell=True)
except Exception as e:
    print(e)

app.include_router(router)


@app.get("/")
async def health_check():
    return "ok"