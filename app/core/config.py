import os
from dotenv import load_dotenv


    
if "APP_ENV" in os.environ and os.environ['APP_ENV'] == 'production':
    load_dotenv('.env')
else:
    load_dotenv('.env.local')

BASE_PATH = os.getenv('BASE_PATH')
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
IMAGE_PATH = os.getenv('IMAGE_PATH')
GCP_AUTH_FILE = os.getenv('GCP_AUTH_FILE')
PROJECT_ID = os.getenv('PROJECT_ID')
CLUSTER_ZONE = os.getenv('CLUSTER_ZONE')

FIREBASE_AUTH_FILE = os.getenv('FIREBASE_AUTH_FILE')

REPO_BUILDER_PATH = os.getenv('REPO_BUILDER_PATH')
REPO_WORKFLOW_ID = os.getenv('REPO_WORKFLOW_ID')

