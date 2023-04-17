from pydantic import BaseModel


class Deploy(BaseModel):
    website_name: str