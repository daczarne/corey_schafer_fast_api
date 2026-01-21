from collections.abc import Sequence
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import Result, select
from sqlalchemy.orm import Session
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.templating import _TemplateResponse

import models
from database import Base, engine, get_db
from schemas import PostCreate, PostResponse, UserCreate, UserResponse


Base.metadata.create_all(bind = engine)


app: FastAPI = FastAPI()
app.mount(path = "/static", app = StaticFiles(directory = "static"), name = "static")
app.mount(path = "/media", app = StaticFiles(directory = "media"), name = "media")

templates = Jinja2Templates(directory = "templates")


#* ########## *#
#* HTML PATHS *#
#* ########## *#

@app.get(path = "/", include_in_schema = False, name = "home")
@app.get(path = "/posts", include_in_schema = False, name = "posts")
def home(
        request: Request,
        db: Annotated[Session, Depends(dependency = get_db)],
    ) -> _TemplateResponse:
    
    result: Result[tuple[models.Post]] = db.execute(statement = select(models.Post))
    posts: Sequence[models.Post] = result.scalars().all()
    
    return templates.TemplateResponse(
        request = request,
        name = "home.html",
        context = {
            "posts": posts,
            "title": "Home",
        },
    )


@app.get(path = "/posts/{post_id}", include_in_schema = False)
def post_page(
        request: Request,
        post_id: int,
        db: Annotated[Session, Depends(dependency = get_db)],
    ) -> _TemplateResponse:
    
    result: Result[tuple[models.Post]] = db.execute(
        statement = select(models.Post).where(models.Post.id == post_id),
    )
    post: models.Post | None = result.scalars().first()
    
    if post:
        title: str = post.title[:50]
        return templates.TemplateResponse(
            request = request,
            name = "post.html",
            context = {
                "post": post,
                "title": title,
            },
        )
    
    raise HTTPException(
        status_code = status.HTTP_404_NOT_FOUND,
        detail = "Post not found",
    )


#* ######### *#
#* API PATHS *#
#* ######### *#

@app.post(
    path = "/api/users",
    response_model = UserResponse,
    status_code = status.HTTP_201_CREATED,
)
def create_user(
        user: UserCreate,
        db: Annotated[Session, Depends(dependency = get_db)],
    ):
    result: Result[tuple[models.User]] = db.execute(
        statement = select(models.User).where(models.User.username == user.username),
    )
    existing_user: models.User | None = result.scalars().first()
    
    if existing_user:
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail = "Username already exists",
        )
    
    result: Result[tuple[models.User]] = db.execute(
        statement = select(models.User).where(models.User.email == user.email),
    )
    existing_email: models.User | None = result.scalars().first()
    
    if existing_email:
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail = "Email already exists",
        )
    
    new_user: models.User = models.User(
        username = user.username,
        email = user.email,
    )
    
    db.add(instance = new_user)
    db.commit()
    db.refresh(instance = new_user)
    
    return new_user


@app.get(path = "/api/users/{user_id}", response_model = UserResponse)
def get_user(
        user_id: int,
        db: Annotated[Session, Depends(dependency = get_db)],
    ):
    result: Result[tuple[models.User]] = db.execute(
        statement = select(models.User).where(models.User.id == user_id),
    )
    user: models.User | None = result.scalars().first()
    
    if user:
        return user
    
    raise HTTPException(
        status_code = status.HTTP_404_NOT_FOUND,
        detail = "User not found",
    )


@app.get(path = "/api/users/{user_id}/posts", response_model = list[PostResponse])
def get_user_posts(
        user_id: int,
        db: Annotated[Session, Depends(dependency = get_db)],
    ):
    result: Result[tuple[models.User]] = db.execute(
        statement = select(models.User).where(models.User.id == user_id),
    )
    user: models.User | None = result.scalars().first()
    
    if not user:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = "User not found",
        )
    
    result2: Result[tuple[models.Post]] = db.execute(
        statement = select(models.Post).where(models.Post.user_id == user_id),
    )
    posts: Sequence[models.Post] = result2.scalars().all()
    return posts


@app.get(path = "/api/posts", response_model = list[PostResponse])
def get_posts(
        db: Annotated[Session, Depends(dependency = get_db)],
    ):
    
    result: Result[tuple[models.Post]] = db.execute(
        statement = select(models.Post),
    )
    posts: Sequence[models.Post] = result.scalars().all()
    return posts


@app.post(
    path = "/api/posts",
    response_model = PostResponse,
    status_code = status.HTTP_201_CREATED,
)
def create_post(
        post: PostCreate,
        db: Annotated[Session, Depends(dependency = get_db)],
    ):
    
    result: Result[tuple[models.User]] = db.execute(
        statement = select(models.User).where(models.User.id == post.user_id),
    )
    user: models.User | None = result.scalars().first()
    
    if not user:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = "User not found",
        )
    
    new_post = models.Post(
        title = post.title,
        content = post.content,
        user_id = post.user_id,
    )
    
    db.add(instance = new_post)
    db.commit()
    db.refresh(instance = new_post)
    return new_post


@app.get(path = "/api/posts/{post_id}", response_model = PostResponse)
def get_post(
        post_id: int,
        db: Annotated[Session, Depends(dependency = get_db)],
    ):
    
    result: Result[tuple[models.Post]] = db.execute(
        statement = select(models.Post).where(models.Post.id == post_id),
    )
    post: models.Post | None = result.scalars().first()
    
    if post:
        return post
    
    raise HTTPException(
        status_code = status.HTTP_404_NOT_FOUND,
        detail = "Post not found",
    )


@app.exception_handler(exc_class_or_status_code = StarletteHTTPException)
def general_http_exception_handler(
        request: Request,
        exception: StarletteHTTPException,
    ) -> JSONResponse | _TemplateResponse:
    
    message: str = (
        exception.detail if exception.detail else "An error occurred. Please check your request and try again."
    )
    
    if request.url.path.startswith("/api"):
        return JSONResponse(
            status_code = exception.status_code,
            content = {
                "detail": message,
            },
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
def validation_exception_handler(
        request: Request,
        exception: RequestValidationError,
    ) -> JSONResponse | _TemplateResponse:
    
    if request.url.path.startswith("/api"):
        return JSONResponse(
            status_code = status.HTTP_422_UNPROCESSABLE_CONTENT,
            content = {
                "detail": exception.errors(),
            },
        )
    
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
