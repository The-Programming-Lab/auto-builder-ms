from pydantic import BaseModel
from app.core.firebase_config import db
from google.api_core.datetime_helpers import DatetimeWithNanoseconds
from fastapi import HTTPException, status


class Website(BaseModel):
    website_id: str
    created_at: DatetimeWithNanoseconds
    description: str
    env: dict
    name: str
    owner_id: str
    port_number: str
    repo_name: str
    updated_at: DatetimeWithNanoseconds

    def save(self):
        data = self.dict(exclude={'website_id'})
        website_ref = db.collection('websites').document(self.website_id)
        website_ref.set(data)
    
    @staticmethod
    def get_from_id(website_id: str):
        website_ref = db.collection('websites').document(website_id)
        try:
            website = website_ref.get().to_dict()
            website["website_id"] = website_id
        except Exception as e:
            print(e)
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Website not found")
        return Website(**website)
    
    @staticmethod
    def get_from_user(website_name: str, user_id: str):
        user_ref = db.collection('users').document(user_id)
        user = user_ref.get().to_dict()
        try :
            website_id = user['websites'][website_name]
            website: Website = Website.get_from_id(website_id)
        except Exception as e:
            print(e)
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Website not found")
        return website


class User(BaseModel):
    user_id: str
    allowed_deployments: int
    created_at: DatetimeWithNanoseconds
    email: str
    fname: str
    github: str
    linkedin: str
    lname: str
    phone: str
    photo_url: str
    role: str
    username: str
    websites: dict

    def save(self):
        data = self.dict(exclude={'user_id'})
        user_ref = db.collection('users').document(self.user_id)
        user_ref.set(data)

    @staticmethod
    def get(user_id: str):
        user_ref = db.collection('users').document(user_id)
        try:
            user = user_ref.get().to_dict()
            user["user_id"] = user_id
        except Exception as e:
            print(e)
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        return User(**user)

class DecodedToken(BaseModel):
    name: str
    picture: str
    iss: str
    aud: str
    auth_time: int
    user_id: str
    sub: str
    iat: int
    exp: int
    email: str
    email_verified: bool
    firebase: dict

    @staticmethod
    def get(decoded_token: dict):
        return DecodedToken(**decoded_token)