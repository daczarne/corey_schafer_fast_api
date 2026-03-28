from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class User(Base):
    __tablename__: str = "users"
    
    id: Mapped[int] = mapped_column(Integer, primary_key = True, index = True)
    username: Mapped[str] = mapped_column(String(length = 50), unique = True, nullable = False)
    email: Mapped[str] = mapped_column(String(length = 120), unique = False, nullable = False)
    password_hash: Mapped[str] = mapped_column(
        String(length = 200),
        unique = False,
        nullable = False,
    )
    image_file: Mapped[str | None] = mapped_column(
        String(length = 200),
        nullable = True,
        default = None,
    )
    
    posts: Mapped[list[Post]] = relationship(
        back_populates = "author",
        cascade = "all, delete-orphan",
    )
    
    @property
    def image_path(self) -> str:
        if self.image_file:
            return f"/media/profile_pics/{self.image_file}"
        
        return f"/static/profile_pics/default.jpg"


class Post(Base):
    __tablename__: str = "posts"
    
    id: Mapped[int] = mapped_column(Integer, primary_key = True, index = True)
    title: Mapped[str] = mapped_column(String(length = 100), nullable = False)
    content: Mapped[str] = mapped_column(Text, nullable = False)
    user_id: Mapped[int] = mapped_column(
        ForeignKey(column = "users.id"),
        nullable = False,
        index = True,
    )
    date_posted: Mapped[datetime] = mapped_column(
        DateTime(timezone = True),
        default = lambda: datetime.now(tz = UTC),
    )
    
    author: Mapped[User] = relationship(back_populates = "posts")
