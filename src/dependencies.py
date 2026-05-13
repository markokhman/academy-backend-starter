"""
DI-фабрики для FastAPI: get_<service>.

Использование в роутах:
    from dependencies import get_user_service

    @router.get("/me")
    async def me(user: Authentication, svc: UserService = Depends(get_user_service)):
        ...
"""

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from database.database import get_session
from services.user import UserService


async def get_user_service(
    session: AsyncSession = Depends(get_session),
) -> UserService:
    return UserService(session)
