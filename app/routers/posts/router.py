from fastapi import APIRouter

from . import delete, get, patch, post, put


router = APIRouter(
    prefix = "/posts",
    tags = ["posts"],
)

router.include_router(router = get.router)
router.include_router(router = post.router)
router.include_router(router = patch.router)
router.include_router(router = put.router)
router.include_router(router = delete.router)
