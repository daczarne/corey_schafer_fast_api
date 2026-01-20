from fastapi import FastAPI, HTTPException, Request, status
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.templating import _TemplateResponse


app: FastAPI = FastAPI()
app.mount(path = "/static", app = StaticFiles(directory = "static"), name = "static")

templates = Jinja2Templates(directory = "templates")


posts: list[dict] = [
    {
        "id": 1,
        "author": "Corey Schafer",
        "title": "FastAPI is awesome",
        "content": "This framework is really easy to use and super fast.",
        "date_posted": "April 20, 2025",
    },
    {
        "id": 2,
        "author": "Jane Doe",
        "title": "Python is great for web development",
        "content": "Python is a great language for web development, and FastAPI makes it even better.",
        "date_posted": "April 21, 2025",
    },
]


@app.get(path = "/", include_in_schema = False, name = "home")
@app.get(path = "/posts", include_in_schema = False, name = "posts")
def home(request: Request) -> _TemplateResponse:
    return templates.TemplateResponse(
        request = request,
        name = "home.html",
        context = {
            "posts": posts,
            "title": "Home",
        },
    )


@app.get(path = "/posts/{post_id}", include_in_schema = False)
def post_page(request: Request, post_id: int) -> _TemplateResponse:
    
    for post in posts:
        if post.get("id") == post_id:
            title: str = post["title"][:50]
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


@app.get(path = "/api/posts")
def get_posts() -> list[dict]:
    return posts


@app.get(path = "/api/posts/{post_id}")
def get_post(post_id: int) -> dict:
    
    for post in posts:
        if post.get("id") == post_id:
            return post
    
    raise HTTPException(
        status_code = status.HTTP_404_NOT_FOUND,
        detail = "Post not found",
    )
