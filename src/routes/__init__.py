from fastapi import APIRouter

from routes.api import router as api_router

main_router = APIRouter()
main_router.include_router(api_router)
