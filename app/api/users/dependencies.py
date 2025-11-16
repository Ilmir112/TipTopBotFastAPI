from datetime import datetime
import logging
from typing import Optional

from fastapi import Depends, Header, Request, HTTPException
from jose import JWTError, jwt

from app.api.users.auth import create_access_token
from app.api.users.dao import SuperUsersDAO, UsersDAO
from app.api.users.models import Users
from app.config import settings
from app.exceptions import (
    IncorrectTokenFormatException,
    TokenAbsentException,
    TokenExpiredException,
    UnauthorizedException,
    UserAlreadyExistsException,
)



async def get_token(
    request: Request,
    authorization: Optional[str] = Header(None),
    token: Optional[str] = None,  # Добавляем параметр запроса для токена
    telegram_id: Optional[int] = None # Добавляем параметр запроса для telegram_id
):
    logging.info("Attempting to get token...")

    # Попытка получить токен из параметра запроса 'token'
    if token:
        logging.info(f"Token found in query parameter: {token[:10]}...")
        return token

    # Попытка получить токен из заголовка Authorization
    if authorization and authorization.startswith("Bearer "):
        token_from_header = authorization[len("Bearer ") :]
        logging.info(f"Token found in Authorization header: {token_from_header[:10]}...")
        return token_from_header

    # Если токена в заголовке нет, попробуем из cookies
    token_from_cookie = request.cookies.get(settings.COOKIE_NAME)
    if token_from_cookie:
        logging.info(f"Token found in cookie '{settings.COOKIE_NAME}': {token_from_cookie[:10]}...")
        return token_from_cookie

    # Если токена нет, но есть telegram_id, генерируем токен

    if request.query_params.get("user_id"):
        telegram_id = request.query_params.get("user_id")
        logging.info(f"Telegram ID found in query parameter: {telegram_id}. Attempting to generate token.")
        user = await UsersDAO.find_one_or_none(telegram_id=int(telegram_id))
        if user:
            access_token = create_access_token({"sub": str(user.telegram_id)})
            logging.info(f"Token generated for telegram_id {telegram_id}: {access_token[:10]}...")
            return access_token
        else:
            logging.warning(f"User with telegram_id {telegram_id} not found. Cannot generate token.")
            raise UnauthorizedException("User not found for provided telegram_id")

    logging.warning("No token found in header, cookies, or query parameters. No telegram_id provided. Raising TokenAbsentException.")
    raise TokenAbsentException # Если токен не найден нигде и telegram_id не предоставлен


async def get_current_user(token: str = Depends(get_token)):
    logging.info("Attempting to get current user...")
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM] # Использовать JWT_SECRET_KEY
        )
        logging.info(f"JWT decoded. Payload: {payload}")
    except JWTError as e:
        logging.error(f"JWTError during decoding: {e}", exc_info=True)
        raise IncorrectTokenFormatException

    expire: str = payload.get("exp")
    logging.info(f"Token expiration (exp): {expire}")
    if (not expire) or (int(expire) < datetime.utcnow().timestamp()):
        logging.warning("Token expired or no expiration found.")
        raise TokenExpiredException

    user_id_str: str = payload.get("sub")
    logging.info(f"User ID (sub) from token: {user_id_str}")
    if not user_id_str:
        logging.warning("No 'sub' in token. Raising UnauthorizedException.")
        raise UnauthorizedException # Если sub отсутствует в токене

    try:
        user_id_int = int(user_id_str)
        logging.info(f"Converted user_id to int: {user_id_int}")
    except ValueError as e:
        logging.error(f"ValueError converting 'sub' to int: {e}", exc_info=True)
        raise IncorrectTokenFormatException # Если sub не является числом

    user = await UsersDAO.find_one_or_none(telegram_id=user_id_int)
    if not user:
        logging.warning(f"User with ID {user_id_int} not found in DB. Raising UnauthorizedException.")
        raise UnauthorizedException # Пользователь не найден

    logging.info(f"Current user {user.telegram_id} retrieved successfully.")
    return user

# Новая функция для входа через Telegram
async def login_via_telegram(telegram_id: int): # Изменена сигнатура
    logging.info(f"Attempting to log in via Telegram for ID: {telegram_id}")
    if telegram_id:
        user_db = await UsersDAO.find_one_or_none(telegram_id=telegram_id)
        if user_db:
            logging.info(f"Telegram user {telegram_id} found in DB. Returning user object.")
            return user_db # Возвращаем объект пользователя
    logging.info(f"Telegram user {telegram_id} not found in DB.")
    return None # Если пользователь не найден


async def get_optional_current_user(request: Request) -> Optional[Users]: # Добавил request: Request
    logging.info("Attempting to get optional current user...")
    try:
        if request.query_params.get('user_id'):
            telegram_id = request.query_params.get('user_id')
        # Поскольку get_token может вызывать исключения, мы должны обрабатывать их здесь.
        token = await get_token(request=request, authorization=request.headers.get("Authorization"), telegram_id=telegram_id)
        logging.info(f"get_optional_current_user: Token obtained: {token[:10]}...")
        user = await get_current_user(token=token)
        logging.info(f"get_optional_current_user: User obtained: {user.telegram_id}")
        return user
    except HTTPException as e:
        logging.info(f"get_optional_current_user: Caught HTTPException: {e.detail} (Status code: {e.status_code}). Returning None.")
        # Если возникло исключение HTTPException (например, TokenAbsentException, UnauthorizedException)
        return None
    except Exception as e:
        logging.error(f"get_optional_current_user: Caught unexpected exception: {e}", exc_info=True)
        return None


async def get_current_admin_user(current_user: Users = Depends(get_current_user)):
    if current_user.access_level not in ["creator", "admin"]:
        raise UserAlreadyExistsException
    return current_user
