from collections.abc import Sequence
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import Result, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models import Post, User
from app.schemas import PostResponse, UserCreate, UserResponse, UserUpdate


router: APIRouter = APIRouter()


@router.post(
    path = "",
    response_model = UserResponse,
    status_code = status.HTTP_201_CREATED,
    tags = ["Users"],
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
    
    query_username: Result[tuple[User]] = await db.execute(
        statement = select(User).where(User.username == user.username),
    )
    existing_username: User | None = query_username.scalars().first()
    
    if existing_username:
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail = "Username already exists",
        )
    
    query_email: Result[tuple[User]] = await db.execute(
        statement = select(User).where(User.email == user.email),
    )
    existing_email: User | None = query_email.scalars().first()
    
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


@router.get(
    path = "/{user_id}",
    response_model = UserResponse,
    tags = ["Users"],
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


@router.patch(
    path = "{user_id}",
    response_model = UserResponse,
    tags = ["Users"],
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
    
    query_user: Result[tuple[User]] = await db.execute(statement = select(User).where(User.id == user_id))
    user: User | None = query_user.scalars().first()
    
    if not user:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = "User not found",
        )
    
    if user_update.username is not None and user_update.username != user.username:
        query_existing_user: Result[tuple[User]] = await db.execute(
            statement = select(User).where(User.username == user_update.username),
        )
        existing_user: User | None = query_existing_user.scalars().first()
        
        if existing_user:
            raise HTTPException(
                status_code = status.HTTP_400_BAD_REQUEST,
                detail = "Username already exists",
            )
    
    if user_update.email is not None and user_update.email != user.email:
        query_existing_email: Result[tuple[User]] = await db.execute(
            statement = select(User).where(User.email == user_update.email),
        )
        existing_email: User | None = query_existing_email.scalars().first()
        
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


@router.delete(
    path = "/{user_id}",
    status_code = status.HTTP_204_NO_CONTENT,
    tags = ["Users"],
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
    
    result: Result[tuple[User]] = await db.execute(statement = select(User).where(User.id == user_id))
    user: User | None = result.scalars().first()
    
    if not user:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = "User not found",
        )
    
    await db.delete(instance = user)
    await db.commit()


@router.get(
    path = "/{user_id}/posts",
    response_model = list[PostResponse],
    tags = ["User Posts"],
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
