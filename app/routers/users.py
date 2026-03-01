from collections.abc import Sequence
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import Post, User
from app.routers.utils import query_posts_by_user_id, query_user_by_email, query_user_by_user_id, query_user_by_username
from app.schemas import PostResponse, UserCreate, UserResponse, UserUpdate


router: APIRouter = APIRouter(
    prefix = "/users",
    tags = ["users"],
)


@router.get(
    path = "/{user_id}",
    response_model = UserResponse,
    summary = "Get a user by `user_id`",
    description = """
        This endpoint fetches the information of an existing user.
    """,
    deprecated = False,
)
async def get_user(
        user_id: int,
        db: Annotated[AsyncSession, Depends(dependency = get_db)],
    ) -> User:
    
    user: User | None = await query_user_by_user_id(user_id = user_id, db = db)
    
    if not user:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = "User not found",
        )
    
    return user


@router.get(
    path = "/{user_id}/posts",
    response_model = list[PostResponse],
    summary = "Get all posts from a given user by `user_id`",
    description = """
        This endpoint fetches all posts associated with a given user.
    """,
    deprecated = False,
)
async def get_user_posts(
        user_id: int,
        db: Annotated[AsyncSession, Depends(dependency = get_db)],
    ) -> Sequence[Post]:
    
    user: User | None = await query_user_by_user_id(user_id = user_id, db = db)
    
    if not user:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = "User not found",
        )
    
    posts: Sequence[Post] = await query_posts_by_user_id(user_id = user_id, db = db)
    
    return posts


@router.delete(
    path = "/{user_id}",
    status_code = status.HTTP_204_NO_CONTENT,
    summary = "Delete a user by `user_id`",
    description = """
        This endpoint deletes a user. All posts associated with that user will also be deleted.
    """,
    deprecated = False,
)
async def delete_user(
        user_id: int,
        db: Annotated[AsyncSession, Depends(dependency = get_db)],
    ) -> None:
    
    user: User | None = await query_user_by_user_id(user_id = user_id, db = db)
    
    if not user:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = "User not found",
        )
    
    await db.delete(instance = user)
    await db.commit()


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
