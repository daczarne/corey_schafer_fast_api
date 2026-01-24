from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import Result, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import User
from app.schemas import UserResponse, UserUpdate


router: APIRouter = APIRouter()


@router.patch(
    path = "{user_id}",
    response_model = UserResponse,
    summary = "Update a user by `user_id` (partial or total update)",
    description = """
        This endpoint updates the attributes of the user.
    """,
    deprecated = False,
)
async def update_user(
        user_id: int,
        user_update: UserUpdate,
        db: Annotated[AsyncSession, Depends(dependency = get_db)],
    ) -> User:
    
    query_user: Result[tuple[User]] = await db.execute(statement = select(User).where(User.id == user_id))
    user: User | None = query_user.scalars().first()
    
    if not user:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = "User not found",
        )
    
    if user_update.username is not None and user_update.username != user.username:
        query_existing_user: Result[tuple[User]] = await db.execute(
            statement = select(User).where(User.username == user_update.username),
        )
        existing_user: User | None = query_existing_user.scalars().first()
        
        if existing_user:
            raise HTTPException(
                status_code = status.HTTP_400_BAD_REQUEST,
                detail = "Username already exists",
            )
    
    if user_update.email is not None and user_update.email != user.email:
        query_existing_email: Result[tuple[User]] = await db.execute(
            statement = select(User).where(User.email == user_update.email),
        )
        existing_email: User | None = query_existing_email.scalars().first()
        
        if existing_email:
            raise HTTPException(
                status_code = status.HTTP_400_BAD_REQUEST,
                detail = "Email already registered",
            )
    
    if user_update.username is not None:
        user.username = user_update.username
    
    if user_update.email is not None:
        user.email = user_update.email
    
    if user_update.image_file is not None:
        user.image_file = user_update.image_file
    
    await db.commit()
    await db.refresh(instance = user)
    
    return user
