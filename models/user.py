from pydantic import BaseModel

class User(BaseModel):
    username: str = None
    email: str = None
    full_name: str = None
    disabled: bool = None

class UserHashed(User):
    hashed_password: str = None

class UserSignup(User):
    password: str