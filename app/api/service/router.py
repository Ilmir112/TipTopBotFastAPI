from app.logger import logger
from datetime import date, datetime

from fastapi import APIRouter, Depends, HTTPException
from fastapi.requests import Request
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError

from app.api.service.models import Service
from app.api.service.schemas import SService
from app.api.users.dependencies import get_current_user
from app.api.users.models import Users
from app.bot.create_bot import bot
from app.api.service.dao import ServiceDAO
from app.bot.keyboards.kbs import main_keyboard
from app.config import settings

router = APIRouter(prefix='/service', tags=['Услуги'])


@router.get("/find_by_id")
async def find_service_by_id(
        service_id: int, user: Users = Depends(get_current_user)):
    result = await ServiceDAO.find_one_or_none(service_id=service_id)
    return result


@router.get("/find_all")
async def find_service_all(user: Users = Depends(get_current_user)):
    try:
        result = await ServiceDAO.find_all()
        return result
    except SQLAlchemyError as db_err:
        msg = f"Database error during find_all: {db_err}"
        logger.error(msg, exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")
    except Exception as e:
        msg = f"Unexpected error during find_all: {str(e)}"
        logger.error(msg, exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")



@router.put("/update_by_id")
async def update_service_data(service_name: str, time_work: int,
        service_id: int,
        user: Users = Depends(get_current_user)
):

    try:
        result = await ServiceDAO.update(
                {"service_id": service_id},
                service_name=service_name,
                time_work=time_work
            )
        return result
    except SQLAlchemyError as db_err:
        msg = f'Database Exception Brigade {db_err}'
        logger.error(msg, extra={"service_name": service_name}, exc_info=True)

    except Exception as e:
        msg = f'Unexpected error: {str(e)}'
        logger.error(msg, extra={"service_name": service_name}, exc_info=True)


@router.post("/add")
async def add_service_data(
        service_data: SService,
        user: Users = Depends(get_current_user)):
    try:
        service = await ServiceDAO.find_one_or_none(service_name=service_data.service_name)

        if service:
            # Уже существует — вернуть ошибку
            raise HTTPException(status_code=409, detail="Service already exists")

        result = await ServiceDAO.add(service_name=service_data.service_name,
                                      time_work=service_data.time_work)
        if result:
            return result
    except SQLAlchemyError as db_err:
        msg = f'Database Exception Brigade {db_err}'
        logger.error(msg, extra={"service_data": service_data.service_name}, exc_info=True)
    except Exception as e:
        msg = f'Unexpected error: {str(e)}'
        logger.error(msg, extra={"service_data": service_data.service_name}, exc_info=True)

@router.delete("/remove")
async def remove_service_data(service_id: int, user: Users = Depends(get_current_user)):
    try:
        result = await ServiceDAO.delete(service_id=service_id)
        return result
    except SQLAlchemyError as db_err:
        msg = f"Database error during remove_service_data: {db_err}"
        logger.error(msg, exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")

    except Exception as e:
        msg = f"Unexpected error during remove_service_data: {str(e)}"
        logger.error(msg, exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


