from fastapi import APIRouter

from .v1 import auth, users

api_v1_router = APIRouter()
api_v1_router.include_router(users.router, prefix="/users", tags=["users"])
api_v1_router.include_router(auth.router, prefix="/auth", tags=["auth"])
