import hashlib
import base64


def encoded_string(user_id: str) -> str:
    user_id_bytes = user_id.encode('utf-8')
    hashed_id = hashlib.sha256(user_id_bytes).digest()
    encoded_id = base64.urlsafe_b64encode(hashed_id).decode('utf-8').rstrip('=')
    return encoded_id.lower()
