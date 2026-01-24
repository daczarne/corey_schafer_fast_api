from collections.abc import Sequence
from contextlib import asynccontextmanager
from typing import Annotated, Any

from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import Result, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session, selectinload
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.templating import _TemplateResponse

from database import Base, engine, get_db
from models import Post, User
from schemas import PostCreate, PostResponse, PostUpdate, UserCreate, UserResponse, UserUpdate


@asynccontextmanager
async def lifespan(_app: FastAPI):
    
    # Startup
    async with engine.begin() as conn:
        await conn.run_sync(fn = Base.metadata.create_all)
    yield
    
    # Shutdown
    await engine.dispose()


app: FastAPI = FastAPI(lifespan = lifespan)
app.mount(path = "/static", app = StaticFiles(directory = "static"), name = "static")
app.mount(path = "/media", app = StaticFiles(directory = "media"), name = "media")

templates = Jinja2Templates(directory = "templates")


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


#* ######### *#
#* API PATHS *#
#* ######### *#

@app.post(
    path = "/api/users",
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
    existing_user: User | None = query_username.scalars().first()
    
    if existing_user:
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


@app.get(
    path = "/api/users/{user_id}",
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


@app.patch(
    path = "/api/users/{user_id}",
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


@app.delete(
    path = "/api/users/{user_id}",
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


@app.get(
    path = "/api/users/{user_id}/posts",
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


@app.get(
    path = "/api/posts",
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


@app.post(
    path = "/api/posts",
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
    await db.refresh(instance = new_post)
    
    return new_post


@app.get(
    path = "/api/posts/{post_id}",
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


@app.put(
    path = "/api/posts/{post_id}",
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
    await db.refresh(instance = post)
    
    return post


@app.patch(
    path = "/api/posts/{post_id}",
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
    await db.refresh(instance = post)
    
    return post


@app.delete(
    path = "/api/posts/{post_id}",
    status_code = status.HTTP_204_NO_CONTENT,
    tags = ["Posts"],
    summary = "Delete a post by `post_id`",
    description = """
        This endpoint deletes the post with the supplied `post_id`.
    """,
    deprecated = False,
)
def delete_post(
        post_id: int,
        db: Annotated[Session, Depends(dependency = get_db)],
    ) -> None:
    
    post: Post | None = db.execute(statement = select(Post).where(Post.id == post_id)).scalars().first()
    
    if not post:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = "Post not found",
        )
    
    db.delete(instance = post)
    db.commit()


#* ########## *#
#* EXCEPTIONS *#
#* ########## *#

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
