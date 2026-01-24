from collections.abc import Sequence
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import Result, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models import Post, User
from app.schemas import PostCreate, PostResponse, PostUpdate


router: APIRouter = APIRouter()


@router.get(
    path = "",
    response_model = list[PostResponse],
    tags = ["Wall"],
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


@router.post(
    path = "",
    response_model = PostResponse,
    status_code = status.HTTP_201_CREATED,
    tags = ["Posts"],
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


@router.get(
    path = "/{post_id}",
    response_model = PostResponse,
    tags = ["Posts"],
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


@router.put(
    path = "/{post_id}",
    response_model = PostUpdate,
    tags = ["Posts"],
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


@router.patch(
    path = "/{post_id}",
    response_model = PostUpdate,
    tags = ["Posts"],
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
    
    query_post: Result[tuple[Post]] = await db.execute(statement = select(Post).where(Post.id == post_id))
    post: Post | None = query_post.scalars().first()
    
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


@router.delete(
    path = "/{post_id}",
    status_code = status.HTTP_204_NO_CONTENT,
    tags = ["Posts"],
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
    
    query_post: Result[tuple[Post]] = await db.execute(statement = select(Post).where(Post.id == post_id))
    post: Post | None = query_post.scalars().first()
    
    if not post:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = "Post not found",
        )
    
    await db.delete(instance = post)
    await db.commit()
