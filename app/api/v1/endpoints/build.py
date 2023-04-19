from fastapi import APIRouter, Depends
import requests
from app.utils.utility import encoded_string
from app.core.config import PROJECT_ID, GITHUB_TOKEN, REPO_BUILDER_PATH, REPO_WORKFLOW_ID
from app.core.security import verify_user
from app.api.v1.models.database import Website, DecodedToken, WebsiteType
from app.core.logging import logger





router = APIRouter(prefix="/github", tags=["GitHub Actions Workflow/Repo"])


@router.post("/build")
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
    env_file = ""
    if website.type == WebsiteType.FRONTEND:
        for key, value in website.env.items():
            env_file += f"{key}={value}\n"

    data = {
        "ref": "main",
        "inputs": {
            "IMAGE_NAME": f"{encoded_id}-{website_name}",
            "PROJECT_ID": PROJECT_ID,
            "BUILD_REPO_NAME": website.repo_name,
            "ENV_FILE": env_file
        }
    }

    # Send the request to trigger the workflow
    response = requests.post(API_ENDPOINT, headers=headers, json=data)
    run_id = response.headers['X-GitHub-Request-Id']

    # Check the response status code
    if response.status_code == 204:
        return {"message": "Workflow dispatched successfully.", "run_id": run_id }
    else:
        logger.error(response.text)
        return {"message": f"Failed to dispatch workflow. Response code: {response.status_code}"}

@router.get("/build/status/{workflow_id}")
async def check_build_done(workflow_id: str, decoded_token: DecodedToken = Depends(verify_user)):
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

# @router.post("/repo")
# async def create_repo(website_name: str, decoded_token: DecodedToken = Depends(verify_user)):
#     org_name = 'The-Programming-Lab'
#     dest_repo = "example"

#     headers = {
#         'Authorization': f'token {GITHUB_TOKEN}',
#         'Accept': 'application/vnd.github+json'
#     }

#     # Create a new repository in the organization
#     api_url = f'https://api.github.com/orgs/{org_name}/repos'
#     repo_data = {
#         'name': dest_repo.split('/')[-1],
#         'private': False,  # Set this to False if you want a public repository
#     }
    
#     response = requests.post(api_url, headers=headers, json=repo_data)
    
#     if response.status_code == 201:
#         print(f'Successfully created the repository: {dest_repo}')
#     else:
#         print(f'Error creating repository: {response.status_code} - {response.text}')
#         return
    

#        # Add topics (labels) to the repository
#     topics_api_url = f'https://api.github.com/repos/{org_name}/{repo_data["name"]}/topics'
#     topics_headers = {
#         'Authorization': f'token {GITHUB_TOKEN}',
#         'Accept': 'application/vnd.github.mercy-preview+json'  # Required for topics API
#     }
#     topics_data = {
#         'names': ['Braeden6'.lower(), 'user-repo']
#     }

#     topics_response = requests.put(topics_api_url, headers=topics_headers, json=topics_data)

#     if topics_response.status_code == 200:
#         print(f'Successfully added topics to the repository: {dest_repo}')
#     else:
#         print(f'Error adding topics: {topics_response.status_code} - {topics_response.text}')





#     src_repo = 'The-Programming-Lab/backend-template'


#         # Import the source repository into the new repository
#     import_api_url = f'https://api.github.com/repos/{org_name}/{repo_data["name"]}/import'
#     import_data = {
#         'vcs_url': f'https://github.com/{src_repo}.git',
#         'vcs': 'git'
#     }
#     import_response = requests.put(import_api_url, headers=headers, json=import_data)

#     if import_response.status_code == 202:
#         print(f'Successfully started importing the contents of {src_repo} to {dest_repo}')
#     else:
#         print(f'Error starting import: {import_response.status_code} - {import_response.text}')
#         return

#     # Check the import status until it's done
#     while True:
#         time.sleep(5)  # Wait for 5 seconds before checking the status again
#         import_status_response = requests.get(import_api_url, headers=headers)

#         if import_status_response.status_code == 200:
#             import_status = import_status_response.json()['status']

#             if import_status == 'complete':
#                 print(f'Successfully imported the contents of {src_repo} to {dest_repo}')
#                 break
#             elif import_status == 'error' or import_status == 'failed':
#                 print(f'Error importing the content: {import_status_response.json()}')
#                 break
#         else:
#             print(f'Error checking import status: {import_status_response.status_code} - {import_status_response.text}')
#             break

#     # Re-enable GitHub Actions for the new repository
#     update_repo_api_url = f'https://api.github.com/repos/{org_name}/{repo_data["name"]}'
#     update_repo_data = {
#         'actions_enabled': True
#     }
#     update_repo_response = requests.patch(update_repo_api_url, headers=headers, json=update_repo_data)

#     if update_repo_response.status_code == 200:
#         print(f'Successfully re-enabled GitHub Actions for the repository: {dest_repo}')
#     else:
#         print(f'Error re-enabling GitHub Actions: {update_repo_response.status_code} - {update_repo_response.text}')



# @router.delete("/repo")
# async def create_repo(website_name: str, decoded_token: DecodedToken = Depends(verify_admin)):
#     repo = 'The-Programming-Lab/example'

#     headers = {
#         'Authorization': f'token {GITHUB_TOKEN}',
#         'Accept': 'application/vnd.github+json'
#     }

#     api_url = f'https://api.github.com/repos/{repo}'
    
#     response = requests.delete(api_url, headers=headers)

#     if response.status_code == 204:
#         print(f'Successfully deleted the repository: {repo}')
#     else:
#         print(f'Error deleting the repository: {response.status_code} - {response.text}')

