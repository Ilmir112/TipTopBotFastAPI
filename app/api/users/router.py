from app.logger import logger

from fastapi import APIRouter, Depends, HTTPException
from starlette.responses import Response

from app.api.users.auth import get_password_hash, authenticate_user, create_access_token
from app.api.users.dependencies import get_current_user, login_via_telegram
from app.api.users.models import SuperUsers
from app.api.users.schemas import SUsers, SUsersRegister, SUsersAuth
from app.bot.create_bot import bot
from app.api.users.dao import UsersDAO, SuperUsersDAO
from app.exceptions import UserAlreadyExistsException, IncorectLoginOrPassword

router = APIRouter(prefix='/auth', tags=["Auth & пользователи"])


@router.post("/register")
async def register_user(user_data: SUsers):
    try:
        existing_user = await UsersDAO.find_one_or_none(username=user_data.username)
        if existing_user:
            bot.send_message("Пользователь уже существует")
            raise UserAlreadyExistsException

        result = await UsersDAO.add(
            first_name=user_data.first_name,
            username=user_data.username,
            telephone_number=user_data.telephone_number
        )
        logger.info("Users adding", extra={"TipTop": user_data.username})
        return result
    except UserAlreadyExistsException:
        logger.warning("Attempt to register existing user", extra={"username": user_data.username})
        raise HTTPException(status_code=400, detail="Пользователь уже существует")
    except Exception as e:
        logger.error('Critical error during registration', exc_info=True)
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера при регистрации")


@router.post("/register_super_user")
async def register_super_user(user_data: SUsersRegister):
    try:
        existing_user = await SuperUsersDAO.find_one_or_none(login_user=user_data.login_user)
        if existing_user:
            raise UserAlreadyExistsException

        hashed_password = get_password_hash(user_data.password)
        result = await SuperUsersDAO.add(
            login_user=user_data.login_user,
            name_user=user_data.name_user,
            surname_user=user_data.surname_user,
            second_name=user_data.second_name,
            password=hashed_password,
            access_level=user_data.access_level,
            telegram_id=user_data.telegram_id,
        )

        logger.info("SuperUser adding", extra={"TipTop": user_data.login_user})
        return result
    except UserAlreadyExistsException:
        logger.warning("Attempt to register existing super user", extra={"login": user_data.login_user})
        raise HTTPException(status_code=400, detail="Пользователь уже существует")
    except Exception as e:
        logger.error(f'Critical error during super user registration {e}', exc_info=True)
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера при регистрации суперпользователя")


@router.post("/login")
async def login_user(response: Response, user_data: SUsersAuth):
    try:
        user = await authenticate_user(user_data.login_user, user_data.password)
        if not user:
            raise IncorectLoginOrPassword

        access_token = create_access_token({"sub": str(user.id)})
        response.set_cookie("access_token", access_token, httponly=True)

        return {
            "login_user": user.login_user,
            "access_token": access_token
        }
    except IncorectLoginOrPassword:
        logger.warning("Invalid login attempt", extra={"login": user_data.login_user})
        raise HTTPException(status_code=401, detail="Неверный логин или пароль")
    except Exception as e:
        logger.error(f'Critical error during login {e}', exc_info=True)
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера при входе")


@router.post("/logout")
async def logout_user(response: Response):
    try:
        response.delete_cookie("access_token")
    except Exception as e:
        logger.error(f'Error during logout {e}', exc_info=True)
    # Возвращаем успешный ответ независимо от ошибок удаления куки
    return {"detail": "Вы успешно вышли"}


@router.get("/me")
async def read_users_me(current_user: SuperUsers = Depends(get_current_user)):
    try:
        return current_user
    except Exception as e:
        logger.error('Error fetching current user', exc_info=True)
        raise HTTPException(status_code=500, detail="Ошибка при получении данных пользователя")


@router.get("/all")
async def read_users_all():
    try:
        users = await UsersDAO.find_all()
        return users
    except Exception as e:
        logger.error('Error fetching all users', exc_info=True)
        raise HTTPException(status_code=500, detail="Ошибка при получении списка пользователей")


@router.get("/find_by_id")
async def read_users_find_by_id(user_id: int):
    try:
        result = await SuperUsersDAO.find_one_or_none_by_id(user_id)
        if not result:
            raise HTTPException(status_code=404, detail="Пользователь не найден")
        return result
    except Exception as e:
        logger.error('Error fetching user by ID', exc_info=True)
        raise HTTPException(status_code=500, detail="Ошибка при получении пользователя по ID")