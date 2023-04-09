from fastapi import APIRouter, Depends
import subprocess
import os
from app.core.config import IMAGE_PATH, CLUSTER_ZONE, PROJECT_ID
import json
from app.core.security import verify_user
from app.core.firebase_config import db
from app.api.v1.models.deploy import Deploy
from app.utils.utility import get_website_by_name

router = APIRouter(prefix="/deploy", tags=["GCP Deployment"])

# !!! files should be unique to the run as if two people are deploying at the same time, the files will be overwritten
def update_yaml_file(file_name, replacement_dict, file_type):
    original_file_name = './app/utils/' + file_name + file_type
    with open(original_file_name, 'r') as file:
        yaml_data = file.read()

    for key, value in replacement_dict.items():
        yaml_data = yaml_data.replace(key, value)

    new_file_name = './app/utils/' + file_name + '_updated' + file_type
    with open(new_file_name, 'w') as file:
        file.write(yaml_data)

    return new_file_name

def apply_yaml_file(file_name, changes, enable_delete=True):
    file = update_yaml_file(file_name, changes, ".yaml")
    # Apply the updated YAML using kubectl
    try :
        subprocess.check_call(f'kubectl apply -f {file}', shell=True)
    except subprocess.CalledProcessError as e:
        print(e)
        return 'error'
    
    if enable_delete and os.path.exists(file):
        os.remove(file)
    
def apply_ingress_file(file_name, changes):
    original_file_name = './app/utils/' + file_name + ".json"
    with open(original_file_name, 'r') as file:
        json_data = file.read()

    for key, value in changes.items():
        json_data = json_data.replace(key, value)
    json_data = json_data.replace('\n', '')
    try :
        subprocess.check_call(f'kubectl patch ingress main --type json -p="{json_data}"', shell=True) 
    except subprocess.CalledProcessError as e:
        print(e)
        return 'error'



# kubectl patch ingress main --type json -p "$(type ingress-add_updated.json)"
# set /p json_patch=<./ingress-add_updated.json

# type ./ingress-add_updated.json > temp_ingress_patch.json



"""
{
    "website_name": "example",
    "cluster_name": "main"
}
"""
@router.post("/container")
async def deployment(input: Deploy, decoded_token: dict = Depends(verify_user)):
    try:
        website = get_website_by_name(input.website_name, decoded_token)
        # get cluster credentials
        subprocess.check_call(f'gcloud container clusters get-credentials {input.cluster_name} --zone={CLUSTER_ZONE} --project={PROJECT_ID}', shell=True) 
        # get most recent image  
        output = subprocess.check_output(f"gcloud container images list-tags us-west1-docker.pkg.dev/{PROJECT_ID}/hello-repo/{website.encoded_id} --format=json --sort-by=timestamp", shell=True)
        output = json.loads(output)
    except subprocess.CalledProcessError as e:
        print(e)
        return 'error'
    image_name = IMAGE_PATH + website.encoded_id + '@' + output[-1]['digest']

    # set env variables for changes in yaml file
    env = website.env
    env_string = ''
    for key, value in env.items():
        # NOTE: The space before the key is important
        env_string += f'          - name: {key}\n            value: {value}\n'

    # make changes to yaml file
    changes = {
        '<deployment-name>': website.encoded_id,
        '<image-name>': image_name,
        '<port-number>': website.port_number,
        # to add env variables
        '<environment-variables>': env_string
    }

    # apply yaml deploy
    apply_yaml_file('deploy', changes)

    return "ok"

# main-client-service 3000 main-client LoadBalancer main2
@router.post("/service")
async def service(service_type: str, cluster_name: str, website_name: str, decoded_token: dict = Depends(verify_user)):
    website = get_website_by_name(website_name, decoded_token)
    try:
        # get cluster credentials
        subprocess.check_call(f'gcloud container clusters get-credentials {cluster_name} --zone={CLUSTER_ZONE} --project={PROJECT_ID}', shell=True) 
    except subprocess.CalledProcessError as e:
        print(e)
        return 'error'

    changes = {
        '<service-name>': website.encoded_id,
        '<port-number>': website.port_number,
        '<deployment-name>': website.encoded_id,
        '<service-type>': service_type,
        '<annotations>': '',
        "<additional-options>": ''
    }

    apply_yaml_file('service', changes)

    return "ok"

@router.post("/rewrite")
async def rewrite(service_type: str, cluster_name: str, website_name: str, decoded_token: dict = Depends(verify_user)):
    website = get_website_by_name(website_name, decoded_token)
    user_ref = db.collection('users').document(decoded_token['uid'])
    username = user_ref.get().to_dict().get('username')
    try:
        # get cluster credentials
        subprocess.check_call(f'gcloud container clusters get-credentials {cluster_name} --zone={CLUSTER_ZONE} --project={PROJECT_ID}', shell=True) 
    except subprocess.CalledProcessError as e:
        print(e)
        return 'error'
    
    changes = {
        '<configmap-name>': website.encoded_id,
        '<config-path>' : f"/user/{username}/{website.name}",
        '<service-name>': website.encoded_id,
        '<deploy-name>': website.encoded_id,
        '<service-type>': service_type
    }

    apply_yaml_file('rewrite', changes)
    # restart rewrite deployment to apply changes
    subprocess.check_call(f'kubectl rollout restart deployment {website.encoded_id}-rewrite', shell=True) 

    return 'ok'


@router.post("/ingress/path")
async def ingress_path_add(website_name: str, cluster_name: str, decoded_token: dict = Depends(verify_user)):
    website = get_website_by_name(website_name, decoded_token)
    user_ref = db.collection('users').document(decoded_token['uid'])
    username = user_ref.get().to_dict().get('username')
    try:
        # get cluster credentials
        subprocess.check_call(f'gcloud container clusters get-credentials {cluster_name} --zone={CLUSTER_ZONE} --project={PROJECT_ID}', shell=True) 
    except subprocess.CalledProcessError as e:
        print(e)
        return 'error'
    
    changes = {
        "<website-path>": f"/user/{username}/{website.name}",
        "<rewrite-service-name>": f"{website.encoded_id}-rewrite-service",
    }
    apply_ingress_file('ingress-add', changes)

    return 'ok'

@router.delete("/ingress/path")
async def ingress_path_remove(website_name: str, cluster_name: str, decoded_token: dict = Depends(verify_user)):
    website = get_website_by_name(website_name, decoded_token)

    try:
        # get cluster credentials
        subprocess.check_call(f'gcloud container clusters get-credentials {cluster_name} --zone={CLUSTER_ZONE} --project={PROJECT_ID}', shell=True) 
    except subprocess.CalledProcessError as e:
        print(e)
        return 'error'
    
    # !!! get index of path to remove
    # !!! kubectl get ingress main -o=jsonpath='{.spec.rules[0].http.paths[*].path}' | tr -s ' ' '\n' | nl | grep '/api2' | awk '{print $1 - 1}
    changes = {
        "<path-index>": "1"
    }
    apply_ingress_file('ingress-remove', changes)


    return 'ok'

@router.put("/ingress/path")
async def ingress_path_update(website_name: str, cluster_name: str, decoded_token: dict = Depends(verify_user)):
    website = get_website_by_name(website_name, decoded_token)
    user_ref = db.collection('users').document(decoded_token['uid'])
    username = user_ref.get().to_dict().get('username')

    try:
        # get cluster credentials
        subprocess.check_call(f'gcloud container clusters get-credentials {cluster_name} --zone={CLUSTER_ZONE} --project={PROJECT_ID}', shell=True) 
    except subprocess.CalledProcessError as e:
        print(e)
        return 'error'
    
    # !!! check if path exists
    # !!! if it does change it 
    changes = {
        "<website-path>": f"/user/{username}/{website.name}",
        "<rewrite-service-name>": f"{website.encoded_id}-rewrite-service",
    }
    apply_ingress_file('ingress-add', changes, '.json')

    return 'ok'





