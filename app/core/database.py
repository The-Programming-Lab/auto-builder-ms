from firebase_admin import credentials, initialize_app, firestore
import os

from app.core.logging import logger



# initialize firebase auth and db
try :
    cred = credentials.Certificate(os.getenv("GOOGLE_KEY_PATH"))
    initialize_app(cred)
    db = firestore.client()
except Exception as e:
    logger.error(e)
    db = None