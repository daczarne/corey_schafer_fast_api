from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import Result, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import Post, User
from app.schemas import PostCreate, PostUpdate


router: APIRouter = APIRouter()


@router.put(
    path = "/{post_id}",
    response_model = PostUpdate,
    summary = "Update a post by `post_id` (full update)",
    description = """
        This endpoint updates all fields in the post with the supplied `post_id` (full update).
    """,
    deprecated = False,
)
async def update_post_full(
        post_id: int,
        post_data: PostCreate,
        db: Annotated[AsyncSession, Depends(dependency = get_db)],
    ) -> Post:
    
    query_post: Result[tuple[Post]] = await db.execute(statement = select(Post).where(Post.id == post_id))
    post: Post | None = query_post.scalars().first()
    
    if not post:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = "Post not found",
        )
    
    if post_data.user_id != post.user_id:
        query_user: Result[tuple[User]] = await db.execute(
            statement = select(User).where(User.id == post_data.user_id),
        )
        user: User | None = query_user.scalars().first()
        
        if not user:
            raise HTTPException(
                status_code = status.HTTP_404_NOT_FOUND,
                detail = "User not found",
            )
    
    post.title = post_data.title
    post.content = post_data.content
    post.user_id = post_data.user_id
    
    await db.commit()
    await db.refresh(
        instance = post,
        attribute_names = ["author"],
    )
    
    return post
