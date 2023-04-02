from fastapi import FastAPI
from app.api.endpoints import build, deploy
import subprocess
from app.api.config import AUTH_FILE_PATH, HEALTH_CHECK_ENDPOINT


app = FastAPI()

# auth gcloud and get cluster
subprocess.check_call(f'gcloud auth activate-service-account --key-file={AUTH_FILE_PATH}', shell=True)

# add router from api/endpoints/example.py
app.include_router(build.router)
app.include_router(deploy.router)



@app.get(HEALTH_CHECK_ENDPOINT)
async def test():
    return "Ok"