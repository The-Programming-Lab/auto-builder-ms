from fastapi import FastAPI
from app.api.endpoints import build, deploy
from app.api.config import health_check_endpoint
import subprocess


app = FastAPI()

cluster_name = 'main'
zone = 'us-central1-b'
project_id = 'the-programming-lab-379219'
auth_file = 'the-programming-lab-379219-2dbd4587e237.json'


# auth gcloud and get cluster
subprocess.check_call(f'gcloud auth activate-service-account --key-file={auth_file}', shell=True)
subprocess.check_call(f'gcloud container clusters get-credentials {cluster_name} --zone={zone} --project={project_id}', shell=True)

# add router from api/endpoints/example.py
app.include_router(build.router)
app.include_router(deploy.router)



@app.get(health_check_endpoint)
async def test():
    return "Ok"