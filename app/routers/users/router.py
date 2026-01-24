from fastapi import APIRouter

from . import delete, get, patch, post


router = APIRouter(
    prefix = "/users",
    tags = ["users"],
)

router.include_router(router = get.router)
router.include_router(router = post.router)
router.include_router(router = patch.router)
router.include_router(router = delete.router)
