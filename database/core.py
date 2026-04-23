from dotenv import load_dotenv
from sqlmodel import create_engine
from sqlalchemy.engine import Engine
import models
import os
load_dotenv()

DB_URL :str = os.getenv("DB_URL", "")
engine : Engine | None = None

async def connect_db():
    global engine
    engine = create_engine(DB_URL)
    print(f"Connected to databsae")

async def close_db():
    global engine
    if engine:
        engine.dispose(close=True)
        print("Database connection closed")

# Return active client
def get_db():
    return engine