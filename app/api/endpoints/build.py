from fastapi import APIRouter
from app.api.config import base_path, hello_world
from app.api.config import GITHUB_TOKEN
import requests

router = APIRouter(prefix=base_path, tags=["example"])


@router.post("/build")
async def start_build(TO_BUILD_REPO: str):
    # return {"message": hello_world}
    # Set up variables for the GitHub repository and workflow
    REPO_OWNER = "The-Programming-Lab"
    REPO_NAME = "user-builder"
    # !!! automatically get the latest workflow id
    # from https://api.github.com/repos/The-Programming-Lab/user-builder/actions/workflows
    WORKFLOW_ID = "52757712"


    # Define the API endpoint and request parameters
    API_ENDPOINT = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/actions/workflows/{WORKFLOW_ID}/dispatches"

    # Set up headers for the API request
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"token {GITHUB_TOKEN}",
        "Content-Type": "application/json"
    }

    # Set up the request data
    data = {
        "ref": "main",
        "inputs": {
            "IMAGE_NAME": TO_BUILD_REPO,
            "PROJECT_ID": "the-programming-lab-379219",
            "BUILD_REPO_NAME": TO_BUILD_REPO
        }
    }

    # Send the request to trigger the workflow
    response = requests.post(API_ENDPOINT, headers=headers, json=data)
    run_id = response.headers['X-GitHub-Request-Id']
    # print(response.workflow_id)

    # Check the response status code
    if response.status_code == 204:
        return {"message": "Workflow dispatched successfully.", "run_id": run_id }
    else:
        return {"message": f"Failed to dispatch workflow. Response code: {response.status_code}"}


@router.get("/build/done")
async def check_build_done(workflow_id: str):
    # Set the GitHub repository and build ID
    repo = 'my-org/my-repo'
    build_id = '123456'

    # Set the GitHub access token (replace with your own token)
    access_token = GITHUB_TOKEN

    # Define the GitHub API endpoint for checking the build status
    url = f'https://api.github.com/repos/{repo}/actions/runs/{build_id}'

    headers = {'Authorization': f'token {access_token}'}

    # Send a GET request to the API endpoint to check the build status
    response = requests.get(url, headers=headers)

    data = response.json()


    return { "message": "Workflow found.", "status": data['status'], "workflow_id": workflow_id }

