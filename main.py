from __future__ import annotations

from typing import TYPE_CHECKING

from fastapi import FastAPI
from fastapi.templating import Jinja2Templates


if TYPE_CHECKING:
    from fastapi import Request
    from starlette.templating import _TemplateResponse


app: FastAPI = FastAPI()

templates: Jinja2Templates = Jinja2Templates(directory = "templates")


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


@app.get(path = "/", include_in_schema = False)
@app.get(path = "/posts", include_in_schema = False)
def home(request: Request) -> _TemplateResponse:
    return templates.TemplateResponse(
        request = request,
        name = "home.html",
    )


@app.get(path = "/api/posts")
def get_posts() -> list[dict]:
    return posts
