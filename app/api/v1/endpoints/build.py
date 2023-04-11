from fastapi import APIRouter, Depends
import requests

from app.utils.utility import encoded_string
from app.core.config import PROJECT_ID, GITHUB_TOKEN, REPO_BUILDER_PATH, REPO_WORKFLOW_ID
from app.core.security import verify_user
from app.core.firebase_config import db
from app.api.v1.models.database import Website, DecodedToken, User





router = APIRouter(prefix="/build", tags=["GitHub Workflow"])


@router.post("/")
async def start_build(website_name: str, decoded_token: DecodedToken = Depends(verify_user)):
    website: Website = Website.get_from_user(website_name, decoded_token.user_id)

    # Define the API endpoint and request parameters
    API_ENDPOINT = f"https://api.github.com/repos/{REPO_BUILDER_PATH}/actions/workflows/{REPO_WORKFLOW_ID}/dispatches"

    # Set up headers for the API request
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"token {GITHUB_TOKEN}",
        "Content-Type": "application/json"
    }

    encoded_id = encoded_string(website.owner_id)
    # Set up the request data
    data = {
        "ref": "main",
        "inputs": {
            "IMAGE_NAME": f"{encoded_id}-{website_name}",
            "PROJECT_ID": PROJECT_ID,
            "BUILD_REPO_NAME": website.repo_name
        }
    }

    # Send the request to trigger the workflow
    response = requests.post(API_ENDPOINT, headers=headers, json=data)
    run_id = response.headers['X-GitHub-Request-Id']

    # Check the response status code
    if response.status_code == 204:
        return {"message": "Workflow dispatched successfully.", "run_id": run_id }
    else:
        return {"message": f"Failed to dispatch workflow. Response code: {response.status_code}"}




@router.get("/done")
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

