from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import Result, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import User
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
    
    query_username: Result[tuple[User]] = await db.execute(
        statement = select(User).where(User.username == user.username),
    )
    existing_username: User | None = query_username.scalars().first()
    
    if existing_username:
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail = "Username already exists",
        )
    
    query_email: Result[tuple[User]] = await db.execute(
        statement = select(User).where(User.email == user.email),
    )
    existing_email: User | None = query_email.scalars().first()
    
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
