from fastapi import APIRouter

from app.api.endpoints import run


api_router = APIRouter()

api_router.include_router(run.router)