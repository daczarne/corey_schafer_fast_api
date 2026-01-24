from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import Result, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import Post, User
from app.schemas import PostCreate, PostResponse


router: APIRouter = APIRouter()


@router.post(
    path = "/",
    response_model = PostResponse,
    status_code = status.HTTP_201_CREATED,
    tags = ["posts"],
    summary = "Create a new post",
    description = """
        This endpoint creates a new post.
    """,
    deprecated = False,
)
async def create_post(
        post: PostCreate,
        db: Annotated[AsyncSession, Depends(dependency = get_db)],
    ) -> Post:
    
    query_user: Result[tuple[User]] = await db.execute(statement = select(User).where(User.id == post.user_id))
    user: User | None = query_user.scalars().first()
    
    if not user:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = "User not found",
        )
    
    new_post: Post = Post(
        title = post.title,
        content = post.content,
        user_id = post.user_id,
    )
    
    db.add(instance = new_post)
    await db.commit()
    await db.refresh(
        instance = new_post,
        attribute_names = ["author"],
    )
    
    return new_post
