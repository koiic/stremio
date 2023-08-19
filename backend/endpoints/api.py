
from fastapi import APIRouter

import movies, auth

router = APIRouter()

router.include_router(movies.router, prefix="/api/v1")
router.include_router(auth.router, prefix="/api/v1")
