import os
from datetime import timedelta
from database import connect_db, close_db
from dotenv import load_dotenv
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
from auth import authenticate_user, create_access_token
from models import Prompt, Response, Token
from rag import load_rag
from users import router as user_router
from contextlib import asynccontextmanager
load_dotenv()

SECRET_KEY=os.getenv("SECRET_KEY")
ALGORITHM=os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES=30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

app = FastAPI()
app.include_router(user_router)
chain = load_rag()

@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_db()
    yield
    await close_db()

@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Incorrect username or password", headers={"WWW-Authenticate": "Bearer"})
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.post("/rag_chain")
async def rag_chain(prompt: Prompt, token: str = Depends(oauth2_scheme)):
    answer = ""
    prompt_dump = prompt.model_dump()
    try:
        for chunk in chain.stream(prompt_dump):
            answer += chunk
    except Exception as e:
        answer = f"Error: {e}"

    return Response(answer).model_dump()
