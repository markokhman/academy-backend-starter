"""
Стандартный формат ответа: {success, message, data}.
Тот же что в appss-back.

Использование:
    return ApiResult(data=user_payload)
    return ApiResult(success=False, message="Not found")
"""

from typing import Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class ApiResult(BaseModel, Generic[T]):
    success: bool = True
    message: str | None = None
    data: T | None = None
