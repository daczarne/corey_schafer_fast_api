from fastapi import FastAPI
from fastapi.responses import HTMLResponse


app: FastAPI = FastAPI()


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


@app.get(path = "/", response_class = HTMLResponse)
@app.get(path = "/posts", response_class = HTMLResponse)
def home() -> str:
    return f"<h1>{posts[0]["title"]}</h1>"


@app.get(path = "/api/posts")
def get_posts() -> list[dict]:
    return posts
