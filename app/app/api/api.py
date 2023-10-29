from fastapi import APIRouter

from app.api.endpoints import talk, users

api_router = APIRouter()
api_router.include_router(talk.router, prefix='/talk', tags=['talk'])
api_router.include_router(users.router, prefix='/chat', tags=['users'])