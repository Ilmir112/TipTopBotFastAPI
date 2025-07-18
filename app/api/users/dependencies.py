from datetime import datetime
from typing import Optional

from fastapi import Depends, Header, Request
from jose import JWTError, jwt

from app.api.users.auth import create_access_token
from app.api.users.dao import SuperUsersDAO
from app.api.users.models import Users
from app.config import settings
from app.exceptions import (
    IncorrectTokenFormatException,
    TokenAbsentException,
    TokenExpiredException,
    UnauthorizedException,
    UserAlreadyExistsException,
)


async def get_token(request: Request, authorization: Optional[str] = Header(None)):

    # Попытка получить токен из заголовка Authorization
    if authorization and authorization.startswith("Bearer "):
        return authorization[len("Bearer ") :]

    # Если токена в заголовке нет, попробуем из cookies
    token = request.cookies.get("access_token")
    if token:
        return token
    token = await login_via_telegram(authorization)
    if token:
        return token
    if not token:
        raise TokenAbsentException


async def get_current_user(token: str = Depends(get_token)):
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
    except JWTError:
        raise IncorrectTokenFormatException

    expire: str = payload.get("exp")
    if (not expire) or (int(expire) < datetime.utcnow().timestamp()):
        raise TokenExpiredException

    user_id: str = payload.get("sub")
    if not user_id:
        raise UserAlreadyExistsException
    if user_id is None:
        user_id = await SuperUsersDAO.find_one_or_none_by_id(int(user_id))
        if not user_id:
            raise UserAlreadyExistsException

    return user_id


# Новая функция для входа через Telegram
async def login_via_telegram(telegram_id: int):

    # Проверяем, что это админ
    if telegram_id not in settings.ADMIN_LIST:
        raise UnauthorizedException
        return None

    # Создаем данные для токена
    data = {
        "sub": str(telegram_id),
        "access_level": "admin",
        # Можно добавить дополнительные поля по необходимости
    }

    # Создаем токен с особым алгоритмом или данными
    token = create_access_token(data)

    # Сохраняем токен в базе данных (предположим, есть метод для этого)
    # await save_token_in_db(user_id=telegram_id, token=token)

    return token


async def get_current_admin_user(current_user: Users = Depends(get_current_user)):
    if current_user.access_level not in ["creator", "admin"]:
        raise UserAlreadyExistsException
    return current_user
