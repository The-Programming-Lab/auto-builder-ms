from fastapi import APIRouter, Depends, HTTPException
import subprocess
import os
import json


from app.core.config import IMAGE_PATH, CLUSTER_ZONE, PROJECT_ID
from app.utils.utility import encoded_string
from app.core.security import verify_user
from app.core.firebase_config import db
from app.api.v1.models.deploy import Deploy
from app.api.v1.models.database import Website, User, DecodedToken


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

def create_namespace(namespace_name):
    try:
        subprocess.check_output(f'kubectl get namespace {namespace_name}', shell=True) 
    except subprocess.CalledProcessError as e:
        subprocess.check_call(f'kubectl create namespace {namespace_name}', shell=True)

def get_cluster(cluster_name):
    try:
        subprocess.check_call(f'gcloud container clusters get-credentials {cluster_name} --zone={CLUSTER_ZONE} --project={PROJECT_ID}', shell=True) 
    except subprocess.CalledProcessError as e:
        print(e)
        raise HTTPException(status_code=404, detail="Cluster not found")

def get_most_recent_image(website: Website) -> str:
    image_name = f"{encoded_string(website.owner_id)}-{website.name}"
    try: 
        output = subprocess.check_output(f"gcloud container images list-tags us-west1-docker.pkg.dev/{PROJECT_ID}/hello-repo/{image_name} --format=json --sort-by=timestamp", shell=True)
        output = json.loads(output)
        full_image_name = IMAGE_PATH + image_name + '@' + output[-1]['digest']
    except subprocess.CalledProcessError as e:
        print(e)
        raise HTTPException(status_code=404, detail="Image not found")
    return full_image_name



@router.post("/")
async def deploy(input: Deploy, decoded_token: DecodedToken = Depends(verify_user)):
    website: Website = Website.get_from_user(input.website_name, decoded_token.user_id)
    user: User = User.get(decoded_token.user_id)

    get_cluster(input.cluster_name)
    image_name = get_most_recent_image(website)

    env_string = ''
    for key, value in website.env.items():
        # NOTE: The space before the key is important
        env_string += f'          - name: {key}\n            value: {value}\n'

    namespace = encoded_string(website.owner_id)
    changes = {
        '<deployment-name>': website.name,
        '<image-name>': image_name,
        '<port-number>': website.port_number,
        # to add env variables
        '<environment-variables>': env_string,
        "<namespace-name>": namespace,
        "<username-label>": user.username,
        "<website-label>": website.name,
    }

    create_namespace(namespace)
    apply_yaml_file('deploy', changes)


    changes = {
        '<service-name>': website.name,
        '<port-number>': website.port_number,
        '<deployment-name>': website.name,
        '<service-type>': input.main_service_type,
        '<annotations>': '',
        "<additional-options>": '',
        "<namespace-name>": namespace,
        "<username-label>": user.username,
        "<website-label>": website.name,
    }

    apply_yaml_file('service', changes)


    encoded_id = encoded_string(website.owner_id)
    rewrite_name = f"rewrite-{encoded_id}"
    changes = {
        '<config-path>' : f"/user/{user.username}/{website.name}",
        '<service-name>': f"{website.name}.{namespace}.svc.cluster.local",

        '<configmap-name>': encoded_id,
        '<rewrite-service-name>': rewrite_name,
        '<rewrite-deploy-name>': rewrite_name,
        '<service-type>': input.rewrite_service_type,
        "<username-label>": user.username,
        "<namespace-name>": "default"
    }

    apply_yaml_file('rewrite', changes, enable_delete=False)
    # restart rewrite deployment to apply changes
    subprocess.check_call(f"kubectl rollout restart deployment {rewrite_name}", shell=True) 

     
    return "ok"



"""
{
    "website_name": "example",
    "cluster_name": "main"
}
"""
@router.post("/container")
async def deployment(input: Deploy, decoded_token: DecodedToken = Depends(verify_user)):
    website: Website = Website.get_from_user(input.website_name, decoded_token.user_id)
    user: User = User.get(decoded_token.user_id)

    get_cluster(input.cluster_name)
    image_name = get_most_recent_image(website)

    env_string = ''
    for key, value in website.env.items():
        # NOTE: The space before the key is important
        env_string += f'          - name: {key}\n            value: {value}\n'

    namespace = encoded_string(website.owner_id)
    changes = {
        '<deployment-name>': website.name,
        '<image-name>': image_name,
        '<port-number>': website.port_number,
        # to add env variables
        '<environment-variables>': env_string,
        "<namespace-name>": namespace,
        "<username-label>": user.username,
        "<website-label>": website.name,
    }

    create_namespace(namespace)
    apply_yaml_file('deploy', changes)

    return "ok"

# main-client-service 3000 main-client LoadBalancer main2
@router.post("/service")
async def service(input: Deploy, decoded_token: DecodedToken = Depends(verify_user)):
    website: Website = Website.get_from_user(input.website_name, decoded_token.user_id)
    user: User = User.get(decoded_token.user_id)

    get_cluster(input.cluster_name)

    env_string = ''
    for key, value in website.env.items():
        # NOTE: The space before the key is important
        env_string += f'          - name: {key}\n            value: {value}\n'

    namespace = encoded_string(website.owner_id)
    changes = {
        '<service-name>': website.name,
        '<port-number>': website.port_number,
        '<deployment-name>': website.name,
        '<service-type>': input.main_service_type,
        '<annotations>': '',
        "<additional-options>": '',
        "<namespace-name>": namespace,
        "<username-label>": user.username,
        "<website-label>": website.name,
    }

    create_namespace(namespace)
    apply_yaml_file('service', changes)

    return "ok"

@router.post("/rewrite")
async def rewrite(input: Deploy, decoded_token: DecodedToken = Depends(verify_user)):
    website: Website = Website.get_from_user(input.website_name, decoded_token.user_id)
    user: User = User.get(decoded_token.user_id)

    get_cluster(input.cluster_name)
    

    # !!! add soon
    path = {}
    for key, id in user.get('websites').items():
        path[f"/user/{user.get('username')}/{key}"] = f"{key}.{user.get('username').lower()}.svc.cluster.local"


    namespace = encoded_string(website.owner_id)
    encoded_id = encoded_string(website.owner_id)
    rewrite_name = f"rewrite-{encoded_id}"
    changes = {
        '<config-path>' : f"/user/{user.username}/{website.name}",
        '<service-name>': f"{website.name}.{namespace}.svc.cluster.local",

        '<configmap-name>': encoded_id,
        '<rewrite-service-name>': rewrite_name,
        '<rewrite-deploy-name>': rewrite_name,
        '<service-type>': input.rewrite_service_type,
        "<username-label>": user.username,
        "<namespace-name>": "default"
    }

    apply_yaml_file('rewrite', changes, enable_delete=False)
    # restart rewrite deployment to apply changes
    subprocess.check_call(f"kubectl rollout restart deployment {rewrite_name}", shell=True) 
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
        "<website-path>": f"/user/{username}",
        "<rewrite-name>": f"{username.lower()}-rewrite",
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
        "<rewrite-service-name>": f"{website.name}-rewrite",
    }
    apply_ingress_file('ingress-add', changes, '.json')

    return 'ok'





