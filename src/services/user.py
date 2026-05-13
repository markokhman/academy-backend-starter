"""
Бизнес-логика юзеров.

Сервис умеет создавать/обновлять/искать юзеров.
В роутах не пиши SQL напрямую — используй методы сервиса.
"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.telegram import TgUser
from models.user import User


class UserService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_tg_id(self, tg_id: int) -> User | None:
        stmt = select(User).where(User.tg_id == tg_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def upsert_from_tg(self, tg_user: TgUser) -> User:
        """Зарегистрировать нового или обновить существующего юзера по данным из Telegram."""
        user = await self.get_by_tg_id(tg_user.id)
        if user is None:
            user = User(
                tg_id=tg_user.id,
                first_name=tg_user.first_name,
                last_name=tg_user.last_name,
                username=tg_user.username,
                language_code=tg_user.language_code,
                is_premium=tg_user.is_premium,
                photo_url=tg_user.photo_url,
            )
            self.session.add(user)
            await self.session.flush()
            await self.session.refresh(user)
            return user

        # Обновляем поля, которые могут меняться
        user.first_name = tg_user.first_name
        user.last_name = tg_user.last_name
        user.username = tg_user.username
        user.language_code = tg_user.language_code
        user.is_premium = tg_user.is_premium
        if tg_user.photo_url:
            user.photo_url = tg_user.photo_url
        await self.session.flush()
        return user
