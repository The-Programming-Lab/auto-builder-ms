from fastapi import FastAPI
from app.api.endpoints import build, deploy, create
import subprocess
from app.api.config import AUTH_FILE_PATH, HEALTH_CHECK_ENDPOINT, FIREBASE_AUTH_FILE, FIREBASE_DB_URL
from firebase_admin import credentials
import firebase_admin

app = FastAPI()

# auth gcloud and get cluster
subprocess.check_call(f'gcloud auth activate-service-account --key-file={AUTH_FILE_PATH}', shell=True)

# initialize firebase auth and db
cred = credentials.Certificate('./' + FIREBASE_AUTH_FILE)
firebase_admin.initialize_app(cred, {
    'databaseURL': FIREBASE_DB_URL
})

# add router from api/endpoints/example.py
app.include_router(build.router)
app.include_router(deploy.router)
app.include_router(create.router)



@app.get(HEALTH_CHECK_ENDPOINT)
async def test():
    return "Ok"