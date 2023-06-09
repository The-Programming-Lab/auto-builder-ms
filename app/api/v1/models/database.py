from pydantic import BaseModel
from typing import Optional
from google.api_core.datetime_helpers import DatetimeWithNanoseconds
from fastapi import HTTPException, status
import uuid
from enum import Enum

from app.core.logging import logger
from app.core.database import db

class NewVariable(BaseModel):
    name: str
    value: str

class WebsiteType(str, Enum):
    FRONTEND = "frontend"
    BACKEND = "backend"


class NewWebsite(BaseModel):
    description: str
    repo_name: str
    port_number: Optional[str] = None
    type: WebsiteType


class Website(BaseModel):
    website_id: Optional[str]
    created_at: DatetimeWithNanoseconds
    description: str
    env: dict
    name: str
    owner_id: str
    port_number: str
    repo_name: str
    type: WebsiteType
    updated_at: Optional[DatetimeWithNanoseconds]

    def save(self):
        data = self.dict(exclude={'website_id'})
        website_ref = db.collection('websites').document(self.website_id)
        website_ref.set(data)

    def to_dict(self):
        return self.dict(exclude={'env'})
    
    def delete(self):
        website_ref = db.collection('websites').document(self.website_id)
        website_ref.delete()

    @staticmethod
    def create(website_data: dict) -> 'Website':
        new_website_id = str(uuid.uuid4())
        website_data["website_id"] = new_website_id
        new_website = Website(**website_data)
        new_website.save()
        return new_website
    
    @staticmethod
    def get_from_id(website_id: str):
        website_ref = db.collection('websites').document(website_id)
        try:
            website = website_ref.get().to_dict()
            website["website_id"] = website_id
        except Exception as e:
            logger.error(e)
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
            logger.error(e)
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
            logger.error(e)
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        return User(**user)
    
    @staticmethod
    def get_from_username(username: str) -> 'User':
        users_ref = db.collection('users')
        users = users_ref.where('username', '==', username).stream()
        for user in users:
            return User.get(user.id)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

# !!! verify which one are not actually optional
class DecodedToken(BaseModel):
    name: Optional[str] = None
    picture: Optional[str] = None
    iss: Optional[str] = None
    aud: Optional[str] = None
    auth_time: Optional[int] = None
    user_id: str
    sub: Optional[str] = None
    iat: Optional[int] = None
    exp: Optional[int] = None
    email: Optional[str] = None
    email_verified: Optional[bool] = None
    firebase: dict

    @staticmethod
    def get(decoded_token: dict):
        return DecodedToken(**decoded_token)