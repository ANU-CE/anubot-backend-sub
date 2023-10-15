from fastapi import APIRouter

from app.api.endpoints.talk import talk

api_router = APIRouter()
api_router.include_router(talk.router, prefix='/api/v1', tags=['talk'])
api_router.include_router(users.router, prefix='/api/v1', tags=['users'])