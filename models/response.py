from pydantic import BaseModel, Field
import uuid

class Response(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    role:str = "user"
    message:str

    def __init__(self, answer: str, **kwargs):
        super().__init__(message=answer, **kwargs)