"""
GET /api/me — текущий юзер.
"""

from fastapi import APIRouter, Depends, HTTPException

from dependencies import get_user_service
from schemas import ApiResult, UserBase
from services.authentication import Authentication
from services.user import UserService

router = APIRouter(tags=["User"])


@router.get("/me")
async def get_me(
    tg_user: Authentication,
    user_service: UserService = Depends(get_user_service),
) -> ApiResult[UserBase]:
    user = await user_service.get_by_tg_id(tg_user.id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not registered. Call /api/auth/verify first.")
    return ApiResult(data=UserBase.model_validate(user))
