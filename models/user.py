from pydantic import EmailStr, BaseModel
from sqlmodel import Field, SQLModel
"""
    Keep Pydantic models seperate from SQLModel models
"""

class User(BaseModel):
    """
        Basic pydantic model for User Object Validation
        Safe to return in the response to client
    """
    username: str 
    email: str 
    full_name: str 
    disabled: bool 


class UserHashed(User):
    hashed_password: str 

class UserSignup(User):
    """
        Temporary model to store User before hashing
        Never return to client
    """
    password: str 

class UserDB(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    username : str = Field(index=True)
    email : EmailStr = Field(index=True)
    full_name : str | None = None
    hashed_password : str = Field(nullable=False)

    def __init__(self, user_hash : UserHashed):
        self.hashed_password = user_hash.hashed_password


