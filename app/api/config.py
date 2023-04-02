import os
from dotenv import load_dotenv


def get_env_var(var_name: str) -> str:
    if "APP_ENV" in os.environ and os.environ['APP_ENV'] == 'production':
        return os.environ[var_name]
    else:
        return os.getenv(var_name)
    
if "APP_ENV" in os.environ and os.environ['APP_ENV'] == 'production':
    get_func = get_env_var
else:
    load_dotenv('.env')
    get_func = os.getenv

HELLO_WORLD = get_func('HELLO_WORLD')
HEALTH_CHECK_ENDPOINT = get_func('HEALTH_CHECK_ENDPOINT')
BASE_PATH = get_func('BASE_PATH')
GITHUB_TOKEN = get_func('GITHUB_TOKEN')
IMAGE_PATH = get_func('IMAGE_PATH')
AUTH_FILE_PATH = get_func('AUTH_FILE_PATH')
PROJECT_ID = get_func('PROJECT_ID')
CLUSTER_ZONE = get_func('CLUSTER_ZONE')

