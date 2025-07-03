import logging
from datetime import date, datetime
from http.client import HTTPException

from fastapi import APIRouter, Depends, Query
from fastapi.requests import Request
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import defer

from app.api.applications.router import get_booked_times
from app.api.working_day.dao import WorkingDayDAO
from app.api.working_day.models import WorkingDay
from app.api.users.dependencies import get_current_user
from app.api.users.models import Users
from app.bot.create_bot import bot
from app.api.working_day.schemas import SWorkingDay, WorkingDaysInput
from app.bot.keyboards.kbs import main_keyboard
from app.config import settings

router = APIRouter(
    prefix='/day',
    tags=['Данные по рабочим дням'])



@router.get("/find_by_id")
async def find_working_by_id(
        day_id: int):
    result = await WorkingDayDAO.find_one_or_none(id=day_id)
    return result


@router.get("/find_by_date")
async def find_working_by_date(
        working_day: date):
    result = await WorkingDayDAO.find_one_or_none(working_day=working_day)

    if result:

        return result


@router.get("/find_all")
async def find_working_day_all():
    result = await WorkingDayDAO.find_all()

    if result:
        # Получаем текущую дату
        today = datetime.now().date()

        # Фильтруем рабочие дни: оставляем только те >= сегодня
        valid_days = [day for day in result if day.date >= today]

        result = list(map(lambda x: x.date, valid_days))
        new_dates = []
        for date in result:
            times = await get_booked_times(date)
            if times:
                new_dates.append(date)



        return new_dates


@router.post("/add")
async def add_working_day(request: Request,
                          working_days: list[WorkingDaysInput]):
    working_day_list = []
    try:
        for day in working_days:
            # Предположим, что day — это экземпляр WorkingDaysInput
            # и у него есть поле date типа str или date
            date_value = day.date
            # Если date — строка, преобразуем её в date
            if isinstance(date_value, str):

                date_obj = datetime.strptime(date_value, '%Y-%m-%d').date()
            else:
                date_obj = date_value  # уже дата

            # Теперь ищем по дате
            existing_day = await WorkingDayDAO.find_one_or_none(date=date_obj)
            if not existing_day:
                # Добавляем новую запись
                new_day = await WorkingDayDAO.add(date=date_obj)
                working_day_list.append({"id": new_day.id, "date": new_day.date})
                await bot.send_message(chat_id=settings.ADMIN_ID, text="Рабочие дни успешно добавлены!")

        return {"status": "'success"}
    except SQLAlchemyError as db_err:
        msg = f'Database Exception work_day {db_err}'
        logging.error(msg, extra={"working_day": working_day_list}, exc_info=True)
    except Exception as e:
        msg = f'Unexpected error: {str(e)}'
        logging.error(msg, extra={"working_day": working_day_list}, exc_info=True)


@router.delete("/remove")
async def remove_working_day_data(
        working_day: date = Query(...)
):
    # Найти запись по дате
    working_day_record = await WorkingDayDAO.find_one_or_none(date=working_day)
    if working_day_record:
        await WorkingDayDAO.delete(id=working_day_record.id)
