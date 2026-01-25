from collections.abc import Sequence
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import Post, User
from app.routers.utils import query_posts_by_user_id, query_user_by_user_id
from app.schemas import PostResponse, UserResponse


router: APIRouter = APIRouter()


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
