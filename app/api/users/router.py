from datetime import date, datetime
from app.logger import logger

from fastapi import APIRouter, Depends
from fastapi.requests import Request
from fastapi.responses import JSONResponse
from starlette.responses import Response

from app.api.users.auth import get_password_hash, authenticate_user, create_access_token
from app.api.users.dependencies import get_current_user, login_via_telegram
from app.api.users.models import SuperUsers, UserToken
from app.api.users.schemas import SUsers, SUsersRegister, SUsersAuth
from app.bot.create_bot import bot
from app.api.users.dao import UsersDAO, SuperUsersDAO, UserTokenDao
from app.bot.keyboards.kbs import main_keyboard
from app.config import settings
from app.exceptions import UserAlreadyExistsException, IncorectLoginOrPassword

router = APIRouter(prefix='/auth', tags=["Auth & пользователи"])


@router.post("/register")
async def register_user(user_data: SUsersRegister):
    try:
        existing_user = await SuperUsersDAO.find_one_or_none(login_user=user_data.login_user)
        if existing_user:
            raise UserAlreadyExistsException
        hashed_password = get_password_hash(user_data.password)
        await SuperUsersDAO.add(
            login_user=user_data.login_user,
            name_user=user_data.name_user,
            surname_user=user_data.surname_user,
            second_name=user_data.second_name,
            password=hashed_password,
            access_level=user_data.access_level,
        )
        logger.info("Users adding", extra={"TipTop": user_data.login_user}, exc_info=True)
    except Exception as e:
        logger.error('Critical error', extra=e, exc_info=True)


@router.post("/login")
async def login_user(response: Response, user_data: SUsersAuth):
    user = await authenticate_user(user_data.login_user, user_data.password)
    if not user:
        raise IncorectLoginOrPassword
    access_token = create_access_token({"sub": str(user.id)})
    response.set_cookie("summary_information_access_token", access_token, httponly=True)

    return {"login_user": user.login_user,
            "access_token": access_token}

@router.post("/logout")
async def logout_user(response: Response):
    response.delete_cookie("summary_information_access_token")


@router.get("/me")
async def read_users_me(current_user: SuperUsers = Depends(get_current_user)):
    return current_user


@router.get("/all")
async def read_users_all():
    return await UsersDAO.find_all()


@router.post("/save_token")
async def save_token_in_db(user_id: int, token: str):
    existing_token = await UserTokenDao.find_one_or_none(user_id=user_id)
    token_record = existing_token.scalar_one_or_none()
    if token_record:
        token_record.token = token
        new_token = UserTokenDao.update(
            {"user_id": user_id},
            {"token": token})

    else:
        new_token = UserTokenDao.add(user_id=user_id, token=token)
    return {"new_token": new_token}

@router.get("/get_token")
async def get_token_db(admin_id: int):
    token = await UserTokenDao.find_one_or_none(user_id=admin_id)
    if token:
        return token
