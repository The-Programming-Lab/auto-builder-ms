from fastapi import APIRouter, Depends, HTTPException, status
from google.api_core.datetime_helpers import DatetimeWithNanoseconds
import requests
import re
import subprocess
import os

from app.core.security import verify_user
from app.api.v1.models.database import Website, User, DecodedToken, NewWebsite, NewVariable, WebsiteType
from app.utils.utility import encoded_string
from app.core.logging import logger
from app.api.v1.endpoints.deploy import apply_rewrite_yaml

IMAGE_PATH = os.getenv("IMAGE_PATH")


'''
swap to firestore db

add these rules

rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    // Users can read their own data, but only write their own displayName, email, and photoURL
    match /users/{userId} {
      allow read, update: if request.auth != null && request.auth.uid == userId;
      allow create: if request.auth != null && request.auth.uid == userId
                    && "displayName" in request.resource.data
                    && "email" in request.resource.data
                    && "photoURL" in request.resource.data;
    }

    // Users can create new webapps and read, update, or delete their own webapps
    match /webapps/{webappId} {
      allow create: if request.auth != null && request.resource.data.user_id == request.auth.uid;
      allow read, update, delete: if request.auth != null && resource.data.user_id == request.auth.uid;
    }

    // Users can create new blog posts and read, update, or delete their own blog posts
    match /blogs/{blogId} {
      allow create: if request.auth != null && request.resource.data.user_id == request.auth.uid;
      allow read, update, delete: if request.auth != null && resource.data.user_id == request.auth.uid;
    }

    // Users can read and create comments for any blog post, but only update or delete their own comments
    match /comments/{commentId} {
      allow create: if request.auth != null;
      allow read, update, delete: if request.auth != null && resource.data.user_id == request.auth.uid;
    }

    // Users can create new questions and read, update, or delete their own questions
    match /questions/{questionId} {
      allow create: if request.auth != null && request.resource.data.user_id == request.auth.uid;
      allow read, update, delete: if request.auth != null && resource.data.user_id == request.auth.uid;
    }
  }
}

'''

router = APIRouter(prefix="/website", tags=["Database Action Create/Update/Delete"])

@router.post("/{website_name}")
async def create_website(new_website: NewWebsite, website_name: str, decoded_token: DecodedToken = Depends(verify_user)):
    """
    Create a new website

    ```json
    {
        "name": "my-web-app",
        "description": "A sample web app",
        "repo": "backend-template", # The-Programming-Lab/<repo-name>
        "port_number": 8000, # optional but if not provided, it will be parsed from the Dockerfile
    }
    ```
    """
    user: User = User.get(decoded_token.user_id)
    for website in user.websites.keys():
        if website == website_name:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Website name already exists")
        
    # check if repo exists 
    url = f"https://api.github.com/repos/The-Programming-Lab/{new_website.repo_name}"
    response = requests.get(url)
    if response.status_code != 200:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Repo not found")
    
    # check if dockerfile exists
    url = f"https://raw.githubusercontent.com/The-Programming-Lab/{new_website.repo_name}/main/Dockerfile" 
    response = requests.get(url)
    if response.status_code != 200:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dockerfile not found")
    
    # get port number from dockerfile
    if new_website.port_number is None:
      expose_pattern = re.compile(r'EXPOSE\s+(\d+)', re.IGNORECASE)
      match = expose_pattern.search(response.text)
      port_number = match.group(1)
    else:
      port_number = new_website.port_number

    # check if user has access to repo
    # !!! add if needed
    # headers = {
    #     'Authorization': f'token {GITHUB_TOKEN}',
    #     'Accept': 'application/vnd.github+json',
    # }
    # url = f'https://api.github.com/repos/The-Programming-Lab/{new_website.repo_name}/collaborators/{user.user_id}/permission'
    # response = requests.get(url, headers=headers)
    # if response.status_code != 200:
    #     print(response.json())
    #     permissions = response.json()['permissions']
        
    #     if permissions['admin'] == False and permissions['push'] == False:
    #         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User does not have access to the repo")

    user.allowed_deployments -= 1
    user.save()
    env = {}
    if new_website.type == WebsiteType.FRONTEND:
        env['BASE_PATH'] = f"/user/{user.username}/{website_name}"
    website: Website = Website.create({
        "name": website_name,
        "description": new_website.description,
        "repo_name": new_website.repo_name,
        "port_number": port_number,
        "created_at": DatetimeWithNanoseconds.now(),
        "updated_at": None,
        "env": env,
        "owner_id": user.user_id,
        "type": new_website.type
    })

    user.websites[website_name] = website.website_id
    user.save()
    
    return {"website": website.to_dict()}

@router.get("/")
async def get_all_websites(username: str, decoded_token: DecodedToken = Depends(verify_user)):
    """
    Get all websites
    """
    user: User = User.get_from_username(username)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    return {"websites": user.websites}

@router.get("/{website_name}")
async def get_website(website_name: str, decoded_token: DecodedToken = Depends(verify_user)):
    """
    Get a website by id
    """
    user: User = User.get(decoded_token.user_id)
    website: Website = Website.get_from_id(user.websites[website_name])
    if website is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Website not found")
    return {"website": website.to_dict()}

@router.put("/{website_name}")
async def update_website(new_website: NewWebsite, website_name: str, decoded_token: DecodedToken = Depends(verify_user)):
    """
    Update a website by id

    ```json
    {
        "name": "my-web-app",
        "description": "A sample web app",
        "repo": "backend-template", # The-Programming-Lab/<repo-name>
        "port_number": 8000, # optional
    }
    ```
    """
    user: User = User.get(decoded_token.user_id)
    website: Website = Website.get_from_id(user.websites[website_name])
    if website is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Website not found")
    if decoded_token.user_id != website.owner_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User does not have access to the website")
    website.name = new_website.name
    website.description = new_website.description
    website.repo_name = new_website.repo_name
    website.updated_at = DatetimeWithNanoseconds.now()
    if new_website.port_number is not None:
        website.port_number = new_website.port_number
    website.save()

    return {"website": website.to_dict()}

@router.delete("/{website_name}")
async def delete_website(website_name: str, decoded_token: DecodedToken = Depends(verify_user)):
    """
    Delete a website by id
    """
    user: User = User.get(decoded_token.user_id)
    website: Website = Website.get_from_id(user.websites[website_name])
    user: User = User.get(decoded_token.user_id)
    if website is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Website not found")
    if decoded_token.user_id != website.owner_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User does not have access to the website")
        # remove deployment, service and image
    namespace = encoded_string(user.user_id)
    try:
        subprocess.run(f"kubectl delete deployment {website.name} -n {namespace}", shell=True)
        subprocess.run(f"kubectl delete service {website.name} -n {namespace}", shell=True)
        # delete images

        subprocess.check_output(f"gcloud artifacts docker images delete {IMAGE_PATH}{namespace}-{website.name} -q --delete-tags", shell=True)
    except Exception as e:
        logger.info(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error deleting website")
    # update user
    website.delete()
    user.websites.pop(website.name)
    user.allowed_deployments += 1
    user.save()
    # update rewrite
    apply_rewrite_yaml(user, namespace, user.username)
    return {"message": "Website deleted"}

@router.post("/{website_name}/env")
async def create_env(website_name: str, new_var: NewVariable, decoded_token: DecodedToken = Depends(verify_user)):
    """
    Create a new environment variable

    ```json
    {
        "name": "your-api-key",
        "value": "your-secret-key"
    }
    ```
    """
    user: User = User.get(decoded_token.user_id)
    website: Website = Website.get_from_id(user.websites[website_name])
    if website is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Website not found")
    if decoded_token.user_id != website.owner_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User does not have access to the website")
    if new_var.name in website.env:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Variable already exists")
    website.env[new_var.name] = new_var.value
    website.save()
    return {"message": "New variable created"}

@router.put("/{website_name}/env/{env_key}")
async def update_env(website_name: str, env_key: str, new_value: str, decoded_token: DecodedToken = Depends(verify_user)):
    """
    Update environment variable

    ```json
    {
        "value": "new-secret-key"
    }
    ```
    """
    user: User = User.get(decoded_token.user_id)
    website: Website = Website.get_from_id(user.websites[website_name])
    if website is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Website not found")
    if decoded_token.user_id != website.owner_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User does not have access to the website")
    if env_key not in website.env:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Variable not found")
    website.env[env_key] = new_value
    website.save()
    return {"message": f"Variable {env_key} updated"}

@router.delete("/{website_name}/env/{env_key}")
async def delete_env(website_name: str, env_key: str, decoded_token: DecodedToken = Depends(verify_user)):
    """
    Delete environment variable
    """
    user: User = User.get(decoded_token.user_id)
    website: Website = Website.get_from_id(user.websites[website_name])
    if website is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Website not found")
    if decoded_token.user_id != website.owner_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User does not have access to the website")
    if env_key not in website.env:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Variable not found")
    website.env.pop(env_key)
    website.save()
    return {"message": "Variable deleted"}

@router.get("/{website_name}/env")
async def get_all_env(website_name: str, decoded_token: DecodedToken = Depends(verify_user)):
    """
    Get all environment variables
    """
    user: User = User.get(decoded_token.user_id)
    website: Website = Website.get_from_id(user.websites[website_name])
    if website is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Website not found")
    if decoded_token.user_id != website.owner_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User does not have access to the website")
    keys = []
    for key, _ in website.env.items():
        keys.append(key)
    return {"env": keys}

