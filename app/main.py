from collections.abc import Sequence
from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Request, Response, status
from fastapi.exception_handlers import http_exception_handler, request_validation_exception_handler
from fastapi.exceptions import RequestValidationError
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import Result, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.templating import _TemplateResponse

from app.database import Base, engine, get_db
from app.models import Post, User
from app.routes.posts import router as posts_router
from app.routes.users import router as users_router


@asynccontextmanager
async def lifespan(_app: FastAPI):  # noqa: ANN201
    
    # Startup
    async with engine.begin() as conn:
        await conn.run_sync(fn = Base.metadata.create_all)
    yield
    
    # Shutdown
    await engine.dispose()


app: FastAPI = FastAPI(lifespan = lifespan)
app.mount(path = "/static", app = StaticFiles(directory = "app/static"), name = "static")
app.mount(path = "/media", app = StaticFiles(directory = "app/media"), name = "media")

templates: Jinja2Templates = Jinja2Templates(directory = "app/templates")

app.include_router(router = users_router, prefix = "/api")
app.include_router(router = posts_router, prefix = "/api")


#* ########## *#
#* HTML PATHS *#
#* ########## *#

@app.get(path = "/", include_in_schema = False, name = "home")
@app.get(path = "/posts", include_in_schema = False, name = "posts")
async def home(
        request: Request,
        db: Annotated[AsyncSession, Depends(dependency = get_db)],
    ) -> _TemplateResponse:
    
    posts_query: Result[tuple[Post]] = await db.execute(
        statement = select(Post).options(selectinload(Post.author)),
    )
    posts: Sequence[Post] = posts_query.scalars().all()
    
    return templates.TemplateResponse(
        request = request,
        name = "home.html",
        context = {
            "posts": posts,
            "title": "Home",
        },
    )


@app.get(path = "/posts/{post_id}", include_in_schema = False)
async def post_page(
        request: Request,
        post_id: int,
        db: Annotated[AsyncSession, Depends(dependency = get_db)],
    ) -> _TemplateResponse:
    
    post_query: Result[tuple[Post]] = await db.execute(
        statement = select(Post).options(selectinload(Post.author)).where(Post.id == post_id),
    )
    post: Post | None = post_query.scalars().first()
    
    if not post:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = "Post not found",
        )
    
    return templates.TemplateResponse(
        request = request,
        name = "post.html",
        context = {
            "post": post,
            "title": post.title[:50],
        },
    )


@app.get(path = "/users/{user_id}/posts", include_in_schema = False, name = "user_posts")
async def user_posts_page(
        request: Request,
        user_id: int,
        db: Annotated[AsyncSession, Depends(dependency = get_db)],
    ) -> _TemplateResponse:
    
    query_user: Result[tuple[User]] = await db.execute(statement = select(User).where(User.id == user_id))
    user: User | None = query_user.scalars().first()
    
    if not user:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = "User not found",
        )
    
    query_post: Result[tuple[Post]] = await db.execute(
        statement = select(Post).options(selectinload(Post.author)).where(Post.user_id == user_id),
    )
    posts: Sequence[Post] = query_post.scalars().all()
    
    return templates.TemplateResponse(
        request = request,
        name = "user_posts.html",
        context = {
            "posts": posts,
            "user": user,
            "title": f"{user.username}'s posts",
        },
    )


#* ########## *#
#* EXCEPTIONS *#
#* ########## *#

@app.exception_handler(exc_class_or_status_code = StarletteHTTPException)
async def general_http_exception_handler(
        request: Request,
        exception: StarletteHTTPException,
    ) -> Response | _TemplateResponse:
    
    if request.url.path.startswith("/api"):
        return await http_exception_handler(request = request, exc = exception)
    
    message: str = (
        exception.detail if exception.detail else "An error occurred. Please check your request and try again."
    )
    
    return templates.TemplateResponse(
        request = request,
        name = "error.html",
        context = {
            "status_code": exception.status_code,
            "title": exception.status_code,
            "message": message,
        },
        status_code = exception.status_code,
    )


@app.exception_handler(exc_class_or_status_code = RequestValidationError)
async def validation_exception_handler(
        request: Request,
        exception: RequestValidationError,
    ) -> Response | _TemplateResponse:
    
    if request.url.path.startswith("/api"):
        return await request_validation_exception_handler(request = request, exc = exception)
    
    return templates.TemplateResponse(
        request = request,
        name = "error.html",
        context = {
            "status_code": status.HTTP_422_UNPROCESSABLE_CONTENT,
            "title": status.HTTP_422_UNPROCESSABLE_CONTENT,
            "message": "Invalid request. Please check your input and try again.",
        },
        status_code = status.HTTP_422_UNPROCESSABLE_CONTENT,
    )
