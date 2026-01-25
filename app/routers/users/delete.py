from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import User
from app.routers.utils import query_user_by_user_id


router: APIRouter = APIRouter()


@router.delete(
    path = "/{user_id}",
    status_code = status.HTTP_204_NO_CONTENT,
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
    
    user: User | None = await query_user_by_user_id(user_id = user_id, db = db)
    
    if not user:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = "User not found",
        )
    
    await db.delete(instance = user)
    await db.commit()
