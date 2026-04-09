from fastapi import APIRouter, status, HTTPException
from models.user import UserHashed, UserSignup, User
from database import get_db
from auth import get_password_hash

router = APIRouter(prefix="/users", tags=["users"])

@router.post("/signup", response_model=User, status_code=status.HTTP_201_CREATED)
async def create_user(user_in: UserSignup):
    db = get_db()
    existing_user = await db.Users.find_one({
        "$or" : [{"email": user_in.email},
                 {"username": user_in.username}]
    })

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    password_hash = get_password_hash(user_in.password)

    user = UserHashed(
        username=user_in.username,
        email=user_in.email,
        hashed_password= password_hash,
        full_name=user_in.full_name,
        disabled=user_in.disabled
    )

    result = await db.Users.insert_one(user.model_dump())
    if not result.inserted_id:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create user"
        )

    return User(
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        disabled=user.disabled
    )