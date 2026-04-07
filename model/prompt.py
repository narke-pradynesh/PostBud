from pydantic import BaseModel, Field
import uuid

class Prompt(BaseModel):
    id : str = Field(default_factory=lambda: str(uuid.uuid4()))
    role:str
    message:str

