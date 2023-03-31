from fastapi import APIRouter
from app.api.config import base_path
import subprocess
import os
from app.api.config import IMAGE_NAME

router = APIRouter(prefix=base_path, tags=["example"])


def update_yaml_file(file_name, replacement_dict):
    original_file_name = './app/yaml/' + file_name + '.yaml'
    with open(original_file_name, 'r') as file:
        yaml_data = file.read()

    for key, value in replacement_dict.items():
        yaml_data = yaml_data.replace(key, value)

    new_file_name = './app/yaml/' + file_name + '_updated.yaml'
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


@router.post("/deployment")
async def deployment():
    deployment_name = 'backend-template'
    image_name = IMAGE_NAME
    port_number = '8000'

    env = {
        'HEALTH_CHECK_ENDPOINT': '/health-check',
        'BASE_PATH': '/user/braeden/api',
        'HELLO_WORLD': 'Hello World from local'
    }

    env_string = ''
    for key, value in env.items():
        # NOTE: The space before the key is important
        env_string += f'          - name: {key}\n            value: {value}\n'

    changes = {
        '<deployment-name>': deployment_name,
        '<image-name>': image_name,
        '<port-number>': port_number,
        # to add env variables
        '<environment-variables>': env_string
    }

    apply_yaml_file('deploy', changes)

    return "ok"

@router.post("/service")
async def service():
    # <annotations>
    # cloud.google.com/backend-config: '{"ports": {"http":"api1-backendconfig"}}'

    # <additional-options>
    # backendConfig:
    #   name: api1-backendconfig

    service_name = 'backend-template-service'
    port_number = '8000'
    deployment_name = 'backend-template'
    service_type = 'ClusterIP'

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
