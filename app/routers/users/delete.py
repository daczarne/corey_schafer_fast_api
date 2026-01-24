from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import Result, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import User


router: APIRouter = APIRouter()


@router.delete(
    path = "/{user_id}",
    status_code = status.HTTP_204_NO_CONTENT,
    tags = ["users"],
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
