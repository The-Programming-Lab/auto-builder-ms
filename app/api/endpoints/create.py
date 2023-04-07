from fastapi import APIRouter
from app.api.config import BASE_PATH
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


Collection Structure (v1):
Collection users:

Document {user_id}:
Field displayName: (string) Display name of the user
Field email: (string) Email address of the user
Field photoURL: (string, optional) Profile picture URL of the user
Field created_at: (timestamp) Account creation date and time
Collection webapps:

Document {webapp_id}:
Field user_id: (string) The ID of the user who created the web app
Field name: (string) Name of the web app
Field description: (string) Description of the web app
Field repo: (string) Repository URL of the web app
Field env: (map) Environment variables as key-value pairs
Field created_at: (timestamp) Web app creation date and time
Field updated_at: (timestamp) Web app last update date and time
Collection blogs:

Document {blog_id}:
Field webapp_id: (string) The ID of the web app the blog post is about
Field user_id: (string) The ID of the user who created the blog post
Field title: (string) Title of the blog post
Field content: (string) Content of the blog post
Field created_at: (timestamp) Blog post creation date and time
Field updated_at: (timestamp) Blog post last update date and time
Field upvotes: (integer) Number of upvotes
Field downvotes: (integer) Number of downvotes
Collection comments:

Document {comment_id}:
Field blog_id: (string) The ID of the blog post the comment is related to
Field user_id: (string) The ID of the user who wrote the comment
Field content: (string) Content of the comment
Field created_at: (timestamp) Comment creation date and time
Collection questions:

Document {question_id}:
Field webapp_id: (string) The ID of the web app the question is about
Field user_id: (string) The ID of the user who asked the question
Field title: (string) Title of the question
Field content: (string) Content of the question
Field created_at: (timestamp) Question creation date and time
Field updated_at: (timestamp) Question last update date and time


'''

router = APIRouter(prefix=BASE_PATH + "/website", tags=["Create and Edit Website"])


@router.post("/")
async def create_website():
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
    return {"message": "Hello World"}

@router.get("/")
async def get_all_websites():
    """
    Get all websites
    """
    return {"message": "Hello World"}

@router.get("/{website_id}")
async def get_website(website_id: str):
    """
    Get a website by id
    """
    return {"message": "Hello World"}

@router.put("/{website_id}")
async def update_website(website_id: str):
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
async def delete_website(website_id: str):
    """
    Delete a website by id
    """
    return {"message": "Hello World"}

@router.post("/{website_id}/env")
async def create_env(website_id: str):
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
async def update_env(website_id: str, env_key: str):
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
async def delete_env(website_id: str, env_key: str):
    """
    Delete environment variable
    """
    return {"message": "Hello World"}

@router.get("/{website_id}/env")
async def get_all_env(website_id: str):
    """
    Get all environment variables

    !!! just return a list of keys
    """
    return {"message": "Hello World"}

