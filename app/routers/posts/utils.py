from typing import Annotated

from fastapi import Depends
from sqlalchemy import Result, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models import Post, User


async def query_post_by_post_id(
        post_id: int,
        db: Annotated[AsyncSession, Depends(dependency = get_db)],
    ) -> Post | None:
    
    query: Result[tuple[Post]] = await db.execute(
        statement = select(Post).options(selectinload(Post.author)).where(Post.id == post_id),
    )
    post: Post | None = query.scalars().first()
    
    return post


async def query_user_by_user_id(
        user_id: int,
        db: Annotated[AsyncSession, Depends(dependency = get_db)],
    ) -> User | None:
    
    query_user: Result[tuple[User]] = await db.execute(statement = select(User).where(User.id == user_id))
    user: User | None = query_user.scalars().first()
    
    return user
