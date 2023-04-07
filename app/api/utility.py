from firebase_admin import auth
from firebase_admin import db

def verify_user(token, is_admin=False):
    try:
        decoded_token = auth.verify_id_token(token)
        user_id = decoded_token['user_id']
        role = db.reference(f'{user_id}/role').get()
        if is_admin:
            return role == 'admin'
        return True
    except:
        return False