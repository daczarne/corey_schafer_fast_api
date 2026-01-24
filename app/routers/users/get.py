from collections.abc import Sequence
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import Result, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models import Post, User
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
    
    query_user: Result[tuple[User]] = await db.execute(statement = select(User).where(User.id == user_id))
    user: User | None = query_user.scalars().first()
    
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
    
    query_user: Result[tuple[User]] = await db.execute(statement = select(User).where(User.id == user_id))
    user: User | None = query_user.scalars().first()
    
    if not user:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = "User not found",
        )
    
    query_posts: Result[tuple[Post]] = await db.execute(
        statement = select(Post).options(selectinload(Post.author)).where(Post.user_id == user_id),
    )
    posts: Sequence[Post] = query_posts.scalars().all()
    
    return posts
