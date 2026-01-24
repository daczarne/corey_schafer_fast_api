from collections.abc import Sequence
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import Result, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models import Post
from app.schemas import PostResponse


router: APIRouter = APIRouter()


@router.get(
    path = "/",
    response_model = list[PostResponse],
    summary = "Get all posts for the wall",
    description = """
        This endpoint fetches all posts in the DB.
    """,
    deprecated = False,
)
async def get_posts(
        db: Annotated[AsyncSession, Depends(dependency = get_db)],
    ) -> Sequence[Post]:
    
    query_post: Result[tuple[Post]] = await db.execute(
        statement = select(Post).options(selectinload(Post.author)),
    )
    posts: Sequence[Post] = query_post.scalars().all()
    
    return posts


@router.get(
    path = "/{post_id}",
    response_model = PostResponse,
    summary = "Get a post by `post_id`",
    description = """
        This endpoint returns the post with the supplied `post_id`.
    """,
    deprecated = False,
)
async def get_post(
        post_id: int,
        db: Annotated[AsyncSession, Depends(dependency = get_db)],
    ) -> Post:
    
    query_post: Result[tuple[Post]] = await db.execute(
        statement = select(Post).options(selectinload(Post.author)).where(Post.id == post_id),
    )
    post: Post | None = query_post.scalars().first()
    
    if not post:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = "Post not found",
        )
    
    return post
