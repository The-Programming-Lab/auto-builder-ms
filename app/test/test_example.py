from fastapi.testclient import TestClient
from app.main import app
import firebase_admin
from firebase_admin import credentials, auth
from app.core.config import FIREBASE_AUTH_FILE, TEST_FIREBASE_API_KEY, TEST_FIREBASE_AUTH_DOMAIN
from app.core.config import TEST_FIREBASE_DATABASE_URL, TEST_FIREBASE_STORAGE_BUCKET, TEST_GITHUB_ACCOUNT_USER_ID
from app.core.config import BASE_PATH
import pyrebase


firebase_config = {
    "apiKey": TEST_FIREBASE_API_KEY,
    "authDomain": TEST_FIREBASE_AUTH_DOMAIN,
    "databaseURL": TEST_FIREBASE_DATABASE_URL,
    "storageBucket": TEST_FIREBASE_STORAGE_BUCKET,
}

firebase = pyrebase.initialize_app(firebase_config)

# Initialize the Firebase Admin SDK
if not firebase_admin._apps:
    cred = credentials.Certificate(FIREBASE_AUTH_FILE)
    firebase_admin.initialize_app(cred)



def get_test_user_id_token():
    # Replace 'testUserUid' with the UID of the test user
    test_user_uid = TEST_GITHUB_ACCOUNT_USER_ID
    print(test_user_uid)
    # Generate a custom token for the test user
    custom_token = auth.create_custom_token(test_user_uid).decode('utf-8')

    # Exchange the custom token for an ID token
    user = firebase.auth().sign_in_with_custom_token(custom_token)
    id_token = user['idToken']
    return id_token


client = TestClient(app)


def test_health_check():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == "ok"


def test_token_creation():
    token = get_test_user_id_token()
    assert token is not None
    response = client.get(BASE_PATH + "/website/",
                            headers={"Authorization": "Bearer " + token},
                            params={"username": "Braeden6"})
    assert response.status_code == 200
    assert response.json() == {
                    "websites": {
                        "example": "QVZ5yW7TzrsljPa7PTx6"
                    }
                }