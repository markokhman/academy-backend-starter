"""
POST /api/auth/verify
---------------------
Принимает Telegram initData в заголовке Authorization (base64).
Проверяет подпись.
Регистрирует юзера в БД (или возвращает существующего).
Отдаёт профиль.
"""

from fastapi import APIRouter, Depends

from dependencies import get_user_service
from schemas import ApiResult, UserBase
from services.authentication import Authentication, CurrentInitData
from services.user import UserService

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/verify")
async def verify(
    _: Authentication,
    init_data: CurrentInitData,
    user_service: UserService = Depends(get_user_service),
) -> ApiResult[UserBase]:
    """
    Точка входа авторизации миниапки.
    К моменту вызова Authentication уже проверила подпись initData.
    Нам остаётся только upsert юзера в БД.
    """
    user = await user_service.upsert_from_tg(init_data.user)
    return ApiResult(data=UserBase.model_validate(user))
