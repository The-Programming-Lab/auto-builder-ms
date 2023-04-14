from firebase_admin import credentials, initialize_app, firestore
from app.core.config import FIREBASE_AUTH_FILE



# initialize firebase auth and db
try :
    cred = credentials.Certificate(FIREBASE_AUTH_FILE)
    initialize_app(cred)
    db = firestore.client()
except Exception as e:
    db = None