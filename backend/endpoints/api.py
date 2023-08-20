from fastapi import APIRouter

import sys

sys.path.append("..")

from backend.endpoints import movies, auth

router = APIRouter(
    prefix="/api/v1",
)

router.include_router(movies.router)
router.include_router(auth.router)
