from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import User
from app.routers.users.utils import query_user_by_email, query_user_by_user_id, query_user_by_username
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
    
    user: User | None = await query_user_by_user_id(user_id = user_id, db = db)
    
    if not user:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = "User not found",
        )
    
    if user_update.username is not None and user_update.username != user.username:
        existing_user: User | None = await query_user_by_username(username = user_update.username, db = db)
        
        if existing_user:
            raise HTTPException(
                status_code = status.HTTP_400_BAD_REQUEST,
                detail = "Username already exists",
            )
    
    if user_update.email is not None and user_update.email != user.email:
        existing_email: User | None = await query_user_by_email(email = user_update.email, db = db)
        
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
