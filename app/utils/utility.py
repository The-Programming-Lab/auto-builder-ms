from app.core.firebase_config import db
from app.api.v1.models.database import Website
from fastapi import HTTPException, status





def get_website_by_name(website_name: str, decoded_token: dict) -> Website:
    """
    Get a website by name
    """
    users_ref = db.collection('users')
    user_ref = users_ref.document(decoded_token['uid'])
    user = user_ref.get().to_dict()
    try :
        website_id = user['websites'][website_name]
        website: Website = Website.get(website_id)
    except KeyError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Website not found")
    except Exception as e:
        print(e)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Website not found")
    return website
