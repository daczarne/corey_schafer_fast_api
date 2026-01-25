from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import Post
from app.routers.utils import query_post_by_post_id


router: APIRouter = APIRouter()


@router.delete(
    path = "/{post_id}",
    status_code = status.HTTP_204_NO_CONTENT,
    summary = "Delete a post by `post_id`",
    description = """
        This endpoint deletes the post with the supplied `post_id`.
    """,
    deprecated = False,
)
async def delete_post(
        post_id: int,
        db: Annotated[AsyncSession, Depends(dependency = get_db)],
    ) -> None:
    
    post: Post | None = await query_post_by_post_id(post_id = post_id, db = db)
    
    if not post:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = "Post not found",
        )
    
    await db.delete(instance = post)
    await db.commit()
