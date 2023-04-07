from fastapi import APIRouter
import subprocess
import os
from app.core.config import IMAGE_PATH, BASE_PATH, CLUSTER_ZONE, PROJECT_ID
import json

router = APIRouter(prefix=BASE_PATH, tags=["example"])


def update_yaml_file(file_name, replacement_dict):
    original_file_name = './app/utils/' + file_name + '.yaml'
    with open(original_file_name, 'r') as file:
        yaml_data = file.read()

    for key, value in replacement_dict.items():
        yaml_data = yaml_data.replace(key, value)

    new_file_name = './app/utils/' + file_name + '_updated.yaml'
    with open(new_file_name, 'w') as file:
        file.write(yaml_data)

    return new_file_name

def apply_yaml_file(file_name, changes, enable_delete=True):
    file = update_yaml_file(file_name, changes)
    # Apply the updated YAML using kubectl
    try :
        subprocess.check_call(f'kubectl apply -f {file}', shell=True)
    except subprocess.CalledProcessError as e:
        print(e)
        return 'error'
    
    if enable_delete and os.path.exists(file):
        os.remove(file)

# cluster names: main, main2
# main-client 3000
# backend-template 8000
# auth-ms 8000

@router.post("/deployment")
async def deployment(deployment_name: str, port_number: str, cluster_name: str):
    try:
        # get cluster credentials
        subprocess.check_call(f'gcloud container clusters get-credentials {cluster_name} --zone={CLUSTER_ZONE} --project={PROJECT_ID}', shell=True) 
        # get most recent image  
        output = subprocess.check_output(f"gcloud container images list-tags us-west1-docker.pkg.dev/{PROJECT_ID}/hello-repo/{deployment_name} --format=json --sort-by=timestamp", shell=True)
        output = json.loads(output)
    except subprocess.CalledProcessError as e:
        print(e)
        return 'error'
    image_name = IMAGE_PATH + deployment_name + '@' + output[-1]['digest']
    # set env variables for changes in yaml file
    env = {
        'HEALTH_CHECK_ENDPOINT': '/health-check',
        'BASE_PATH': '/user/braeden/api',
        'HELLO_WORLD': 'Hello World from local'
    }
    env_string = ''
    for key, value in env.items():
        # NOTE: The space before the key is important
        env_string += f'          - name: {key}\n            value: {value}\n'

    # make changes to yaml file
    changes = {
        '<deployment-name>': deployment_name,
        '<image-name>': image_name,
        '<port-number>': port_number,
        # to add env variables
        '<environment-variables>': env_string
    }

    # apply yaml deploy
    apply_yaml_file('deploy', changes)

    return "ok"

# main-client-service 3000 main-client LoadBalancer main2
@router.post("/service")
async def service(service_name: str, port_number: str, deployment_name: str, service_type: str, cluster_name: str):
    # <annotations>
    # cloud.google.com/backend-config: '{"ports": {"http":"api1-backendconfig"}}'

    # <additional-options>
    # backendConfig:
    #   name: api1-backendconfig

    try:
        # get cluster credentials
        subprocess.check_call(f'gcloud container clusters get-credentials {cluster_name} --zone={CLUSTER_ZONE} --project={PROJECT_ID}', shell=True) 
    except subprocess.CalledProcessError as e:
        print(e)
        return 'error'

    changes = {
        '<service-name>': service_name,
        '<port-number>': port_number,
        '<deployment-name>': deployment_name,
        '<service-type>': service_type,
        '<annotations>': '',
        "<additional-options>": ''
    }

    apply_yaml_file('service', changes)

    return "ok"

@router.post("/config-map")
async def config_map():
    deployment_name = 'backend-template'

    env = {
        'HEALTH_CHECK_ENDPOINT': '/health-check',
        'BASE_PATH': '/user/braeden/api',
        'HELLO_WORLD': 'Hello World from local'
    }

    env_string = ''
    for key, value in env.items():
        # NOTE: The space before the key is important
        env_string += f'  {key}: {value}\n'

    changes = {
        '<configmap-name>' : deployment_name + '-configmap',
        '<list-of-environment-variables>': env_string
    }

    apply_yaml_file('configmap', changes)
    
    return 'ok'

@router.post("/backend-config")
async def backend_config():
    # <backendconfig-name>
    # <health-check-path>
    return 'ok'

@router.post("/ingress/path/add")
async def ingres_path_add():
    return 'ok'

@router.post("/ingress/path/remove")
async def ingres_path_remove():
    return 'ok'

@router.post("/ingress/path/update")
async def ingres_path_update():
    return 'ok'
