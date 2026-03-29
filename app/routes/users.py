from collections.abc import Sequence
from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import Result, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import create_access_token, hash_password, oauth2_scheme, verify_access_token, verify_password
from app.config import settings
from app.database import get_db
from app.models import Post, User
from app.routes.utils import query_posts_by_user_id, query_user_by_email, query_user_by_user_id, query_user_by_username
from app.schemas import PostResponse, Token, UserCreate, UserPrivate, UserPublic, UserUpdate


router: APIRouter = APIRouter(
    prefix = "/users",
    tags = ["users"],
)


@router.post(
    path = "/",
    response_model = UserPrivate,
    status_code = status.HTTP_201_CREATED,
    summary = "Create a new user",
    description = "This endpoint creates a new user.",
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
        email = user.email.lower(),
        password_hash = hash_password(user.password),
    )
    
    db.add(instance = new_user)
    await db.commit()
    await db.refresh(instance = new_user)
    
    return new_user


@router.post(
    path = "/token",
    response_model = Token,
    summary = "Login endpoint",
    description = """
        This endpoint checks the user authentication attempt and, if valid, returns a token for the user session.
    """,
    deprecated = False,
)
async def login_for_access_token(
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
        db: Annotated[AsyncSession, Depends(dependency = get_db)],
    ) -> Token:
    
    # Look up user by email (case-insensitive)
    # Note: OAuth2PasswordRequestForm uses "username" field, but we treat it as email
    result: Result[tuple[User]] = await db.execute(
        statement = select(User).where(
            func.lower(User.email) == form_data.username.lower(),
        ),
    )
    
    user: User | None = result.scalars().first()
    
    # Verify user exists and password is correct
    # Don't reveal which one failed (security best practice)
    if not user or not verify_password(plain_password = form_data.password, hashed_password = user.password_hash):
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = "Incorrect email or password",
            headers = {
                "WWW-Authenticate": "Bearer",
            },
        )
    
    # Create access token with user id as subject
    access_token_expires: timedelta = timedelta(minutes = settings.access_token_expire_minutes)
    access_token: str = create_access_token(
        data = {"sub": str(user.id)},
        expires_delta = access_token_expires,
    )
    
    return Token(access_token = access_token, token_type = "bearer")


@router.get(
    path = "/me",
    response_model = UserPrivate,
    summary = "Validate user's token",
    description = "Validates a user's token.",
    deprecated = False,
)
async def get_current_user(
        token: Annotated[str, Depends(dependency = oauth2_scheme)],
        db: Annotated[AsyncSession, Depends(dependency = get_db)],
    ) -> User:
    # Get the currently authenticated user.
    
    user_id: str | None = verify_access_token(token = token)
    
    if user_id is None:
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = "Invalid or expired token",
            headers = {
                "WWW-Authenticate": "Bearer",
            },
        )
    
    # Validate user_id is a valid integer (defense against malformed JWT)
    try:
        user_id_int = int(user_id)
    except (TypeError, ValueError):
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = "Invalid or expired token",
            headers = {
                "WWW-Authenticate": "Bearer",
            },
        )
    
    result: Result[tuple[User]] = await db.execute(
        statement = select(User).where(User.id == user_id_int),
    )
    user: User | None = result.scalars().first()
    if not user:
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = "User not found",
            headers = {
                "WWW-Authenticate": "Bearer",
            },
        )
    
    return user


@router.get(
    path = "/{user_id}",
    response_model = UserPublic,
    summary = "Get a user by `user_id`",
    description = "This endpoint fetches the information of an existing user.",
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
    description = "This endpoint fetches all posts associated with a given user.",
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
    description = "This endpoint deletes a user. All posts associated with that user will also be deleted.",
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
    response_model = UserPrivate,
    summary = "Update a user by `user_id` (partial or total update)",
    description = "This endpoint updates the attributes of the user.",
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
