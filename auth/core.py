import os
from datetime import timedelta, datetime
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from passlib.context import CryptContext
from pymongo import MongoClient

from auth import TokenData
from models import UserHashed
from dotenv import load_dotenv
load_dotenv()

SECRET_KEY=str(os.getenv("SECRET_KEY"))
ALGORITHM=str(os.getenv("ALGORITHM"))
ACCESS_TOKEN_EXPIRE_MINUTES=os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")

# MongoDB Connection Setup
db_client=MongoClient(os.getenv("MONGODB_URI"))
db=db_client[str(os.getenv("DATABASE"))]
collection=db["Users"]

# Auth helpers and utils
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)


def get_user(username: str) -> UserHashed | None:
    user_data = collection.find_one({"username": username})

    if user_data is None:
        return None
    user_data = dict(user_data)
    user_data["id"] = str(user_data.pop("_id"))

    return UserHashed(**user_data)

def authenticate_user(username:str, password:str):
    user = get_user(username)
    if not user:
        return False
    result = verify_password(password, user.hashed_password)
    if not result:
        return False
    return user

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credential_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                         detail="Could not validate credentials", headers={"WWW-Authenticate": "Bearer"})
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credential_exception

        token_data = TokenData(username=username)
    except JWTError:
        raise credential_exception
    user = get_user(username=token_data.username)
    if user is None:
        raise credential_exception

    return user


async def get_current_active_user(current_user: UserHashed = Depends(get_current_user)):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")

    return current_user
