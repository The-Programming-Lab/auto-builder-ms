from firebase_admin import auth
from fastapi import HTTPException, status, Depends
from app.core.firebase_config import db
from fastapi.security import HTTPBearer


http_bearer = HTTPBearer()

def verify_user(bearer: str = Depends(http_bearer)):
    try:
        decoded_token = auth.verify_id_token(bearer.credentials)
        return decoded_token
    except Exception as e:
        print(e)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid access token")

    
def verify_admin(bearer: str = Depends(http_bearer)):
    try:
        decoded_token = auth.verify_id_token(bearer.credentials)
        users_ref = db.collection('users')
        user_ref = users_ref.document(decoded_token['uid'])
        if user_ref.get().to_dict()['role'] == 'admin':
            return decoded_token
    except Exception as e:
        print(e)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid access token")
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="You are not an admin")