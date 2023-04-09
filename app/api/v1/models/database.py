from pydantic import BaseModel
from app.core.firebase_config import db
from google.api_core.datetime_helpers import DatetimeWithNanoseconds


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
    encoded_id: str

    def save(self):
        website_ref = db.collection('websites').document(self.website_id)
        website_ref.set(self.dict())
    
    @staticmethod
    def get(website_id: str):
        website_ref = db.collection('websites').document(website_id)
        website = website_ref.get().to_dict()
        website["website_id"] = website_id
        return Website(**website)
