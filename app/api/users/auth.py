import logging
from datetime import datetime, timedelta

from jose import jwt
from passlib.context import CryptContext

from app.api.users.dao import SuperUsersDAO
from app.config import settings

import hmac
import hashlib

from app.logger import logger

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password, hashed_password) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=1800)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, settings.ALGORITHM)
    return encoded_jwt


def verify_telegram_authorization(data: dict) -> bool:

    try:
        logging.info(f"DEBUG Auth: Incoming data for verification: {data}")
        check_hash = data.pop("hash")
        logging.warning(f"DEBUG Auth: Extracted check_hash: {check_hash}")
        # Исключаем поля со значением None при формировании data_check_string
        filtered_data = {k: v for k, v in data.items() if v is not None}
        data_check_string = "\n".join(sorted([f"{key}={value}" for key, value in filtered_data.items()]))
        logging.info(f"DEBUG Auth: Data check string: {data_check_string}")
        secret_key = hashlib.sha256(settings.BOT_TOKEN.encode()).digest()
        logging.info(f"DEBUG Auth: Secret key (first 10 chars): {secret_key[:10]}")
        hmac_hash = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()
        logging.info(f"DEBUG Auth: Computed HMAC hash: {hmac_hash}")
        is_correct = hmac.compare_digest(hmac_hash, check_hash)
        logging.info(f"DEBUG Auth: HMAC comparison result: {is_correct}")
        return is_correct
    except Exception as e:
        logger.error(f"DEBUG Auth: Error during Telegram authorization verification: {e}", exc_info=True)
        return False


async def authenticate_user(login_user: str, password: str):
    user = await SuperUsersDAO.find_one_or_none(login_user=login_user)

    if user:
        if not verify_password(password, user.password):
            return None

    return user
