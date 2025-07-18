import logging

from fastapi import APIRouter, Depends
from sqlalchemy.exc import SQLAlchemyError

from app.api.masters.dao import MasterDAO
from app.api.masters.models import Master
from app.api.masters.schemas import SMaster
from app.api.users.dependencies import get_current_user
from app.api.users.models import Users

router = APIRouter(prefix="/masters", tags=["Данные по мастерам"])


@router.get("/find_by_id")
async def find_master_by_id(master_id: int, user: Users = Depends(get_current_user)):
    result = await MasterDAO.find_one_or_none(master_id=master_id)
    return result


@router.get("/find_all")
async def find_master_all(user: Users = Depends(get_current_user)):
    result = await MasterDAO.find_all()
    return result


@router.put("/update_by_id")
async def update_master_data(
    master_name: str,
    master_id: Master = Depends(find_master_by_id),
    user: Users = Depends(get_current_user),
):
    try:
        if master_id:
            result = await MasterDAO.update(
                {"id": master_id}, {"master_name": master_name}
            )
            return result
    except SQLAlchemyError as db_err:
        msg = f"Database Exception Brigade {db_err}"
        logging.error(msg, extra={"master_name": master_name}, exc_info=True)

    except Exception as e:
        msg = f"Unexpected error: {str(e)}"
        logging.error(msg, extra={"master_name": master_name}, exc_info=True)


@router.post("/add")
async def add_master_data(
    master_data: SMaster, user: Users = Depends(get_current_user)
):
    try:
        master_name = await MasterDAO.find_one_or_none(
            master_name=master_data.master_name
        )
        if master_name:
            result = await MasterDAO.add(master_name=master_data.master_name)
            return result
    except SQLAlchemyError as db_err:
        msg = f"Database Exception Brigade {db_err}"
        logging.error(
            msg, extra={"master_name": master_data.master_name}, exc_info=True
        )
    except Exception as e:
        msg = f"Unexpected error: {str(e)}"
        logging.error(
            msg, extra={"master_name": master_data.master_name}, exc_info=True
        )
