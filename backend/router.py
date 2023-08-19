from fastapi import APIRouter

from backend import api

router = APIRouter()
router.include_router(api.router)
