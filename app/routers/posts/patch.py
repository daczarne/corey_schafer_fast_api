from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import Post
from app.routers.posts.utils import query_post_by_post_id
from app.schemas import PostUpdate


router: APIRouter = APIRouter()


@router.patch(
    path = "/{post_id}",
    response_model = PostUpdate,
    summary = "Update a post by `post_id` (partial update)",
    description = """
        This endpoint updates the supplied attributes from the post with the supplied `post_id` (partial update).
    """,
    deprecated = False,
)
async def update_post_partial(
        post_id: int,
        post_data: PostUpdate,
        db: Annotated[AsyncSession, Depends(dependency = get_db)],
    ) -> Post:
    
    post: Post | None = await query_post_by_post_id(post_id = post_id, db = db)
    
    if not post:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = "Post not found",
        )
    
    update_data: dict[str, Any] = post_data.model_dump(exclude_unset = True)
    
    for field, value in update_data.items():
        setattr(post, field, value)
    
    await db.commit()
    await db.refresh(
        instance = post,
        attribute_names = ["author"],
    )
    
    return post
