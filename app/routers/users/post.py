from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import User
from app.routers.utils import query_user_by_email, query_user_by_username
from app.schemas import UserCreate, UserResponse


router: APIRouter = APIRouter()


@router.post(
    path = "/",
    response_model = UserResponse,
    status_code = status.HTTP_201_CREATED,
    summary = "Create a new user",
    description = """
        This endpoint creates a new user.
    """,
    deprecated = False,
)
async def create_user(
        user: UserCreate,
        db: Annotated[AsyncSession, Depends(dependency = get_db)],
    ) -> User:
    
    existing_username: User | None = await query_user_by_username(username = user.username, db = db)
    
    if existing_username:
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail = "Username already exists",
        )
    
    existing_email: User | None = await query_user_by_email(email = user.email, db = db)
    
    if existing_email:
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail = "Email already exists",
        )
    
    
    new_user: User = User(
        username = user.username,
        email = user.email,
    )
    
    db.add(instance = new_user)
    await db.commit()
    await db.refresh(instance = new_user)
    
    return new_user
