from fastapi import APIRouter, Depends

from app.core.firebase_config import db
from app.core.security import verify_user, verify_admin
from app.api.v1.models.database import Website, User, DecodedToken

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

router = APIRouter(prefix="/website", tags=["Create and Edit Website"])

@router.post("/")
async def create_website(decoded_token: DecodedToken = Depends(verify_user)):
    """
    Create a new website

    ```json
    {
        "name": "my-web-app",
        "description": "A sample web app",
        "repo": "https://github.com/user/my-web-app.git"
    }
    ```
    """
    print(decoded_token)
    return {"message": "Hello World"}

@router.get("/")
async def get_all_websites(decoded_token: DecodedToken = Depends(verify_user)):
    """
    Get all websites
    """
    return {"message": "Hello World"}

@router.get("/{website_id}")
async def get_website(website_id: str, decoded_token: DecodedToken = Depends(verify_user)):
    """
    Get a website by id
    """
    return {"message": "Hello World"}

@router.put("/{website_id}")
async def update_website(website_id: str, decoded_token: DecodedToken = Depends(verify_user)):
    """
    Update a website by id

    ```json
    {
        "name": "my-web-app",
        "description": "A sample web app",
        "repo": "https://github.com/user/my-web-app.git"
    }
    ```
    """
    return {"message": "Hello World"}

@router.delete("/{website_id}")
async def delete_website(website_id: str, decoded_token: DecodedToken = Depends(verify_user)):
    """
    Delete a website by id
    """
    return {"message": "Hello World"}

@router.post("/{website_id}/env")
async def create_env(website_id: str, decoded_token: DecodedToken = Depends(verify_user)):
    """
    Create a new environment variable

    ```json
    {
        "API_KEY": "your-api-key",
        "SECRET_KEY": "your-secret-key"
    }
    ```
    """
    return {"message": "Hello World"}


@router.put("/{website_id}/env/{env_key}")
async def update_env(website_id: str, env_key: str, decoded_token: DecodedToken = Depends(verify_user)):
    """
    Update environment variable

    ```json
    {
        "value": "new-secret-key"
    }
    ```
    """
    return {"message": "Hello World"}

@router.delete("/{website_id}/env/{env_key}")
async def delete_env(website_id: str, env_key: str, decoded_token: DecodedToken = Depends(verify_user)):
    """
    Delete environment variable
    """
    return {"message": "Hello World"}

@router.get("/{website_id}/env")
async def get_all_env(website_id: str, decoded_token: DecodedToken = Depends(verify_user)):
    """
    Get all environment variables

    !!! just return a list of keys
    """
    return {"message": "Hello World"}

