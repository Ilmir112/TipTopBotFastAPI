from datetime import date, datetime

from fastapi import APIRouter, Query
from fastapi.requests import Request
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError

from app.api.applications.dao import ApplicationDAO
from app.api.applications.router import get_booked_times
from app.api.working_day.dao import WorkingDayDAO
from app.api.working_day.schemas import WorkingDaysInput
from app.bot.create_bot import bot
from app.config import settings
from app.logger import logger

router = APIRouter(prefix="/day", tags=["Данные по рабочим дням"])


@router.get("/find_by_id")
async def find_working_by_id(day_id: int):
    try:
        result = await WorkingDayDAO.find_one_or_none(id=day_id)
        if not result:
            return JSONResponse(
                status_code=404, content={"detail": "Рабочий день не найден"}
            )
        return result
    except SQLAlchemyError as e:
        logger.error(f"Database error in find_working_by_id: {e}", exc_info=True)
        return JSONResponse(status_code=500, content={"detail": "Ошибка базы данных"})
    except Exception as e:
        logger.error(f"Unexpected error in find_working_by_id: {e}", exc_info=True)
        return JSONResponse(
            status_code=500, content={"detail": "Внутренняя ошибка сервера"}
        )


@router.get("/find_by_date")
async def find_working_by_date(working_day: date):
    try:
        result = await WorkingDayDAO.find_one_or_none(working_day=working_day)
        if not result:
            return JSONResponse(
                status_code=404, content={"detail": "Рабочий день не найден"}
            )
        return result
    except SQLAlchemyError as e:
        logger.error(f"Database error in find_working_by_date: {e}", exc_info=True)
        return JSONResponse(status_code=500, content={"detail": "Ошибка базы данных"})
    except Exception as e:
        logger.error(f"Unexpected error in find_working_by_date: {e}", exc_info=True)
        return JSONResponse(
            status_code=500, content={"detail": "Внутренняя ошибка сервера"}
        )


@router.get("/find_applications_by_date")
async def find_applications_by_date(working_day: date):
    try:
        result = await ApplicationDAO.find_all(appointment_date=working_day)
        if not result:
            return {"workingDays": []}
        return {
            "workingDays": list(
                filter(lambda x: (x.appointment_time, x.client_name), result)
            )
        }
    except SQLAlchemyError as e:
        logger.error(f"Database error in find_working_by_date: {e}", exc_info=True)
    except Exception as e:
        logger.error(f"Unexpected error in find_working_by_date: {e}", exc_info=True)


@router.get("/find_all")
async def find_working_day_all():
    try:
        result = await WorkingDayDAO.find_all()
        if not result:
            return []

        today = datetime.now().date()
        valid_days = [day for day in result if day.date >= today]
        dates_list = list(map(lambda x: x.date, valid_days))

        new_dates = []
        for dt in dates_list:
            try:
                times = await get_booked_times(dt)
                if times:
                    new_dates.append(dt)
            except Exception as e:
                logger.error(
                    f"Error fetching booked times for {dt}: {e}", exc_info=True
                )

        return new_dates
    except SQLAlchemyError as e:
        logger.error(f"Database error in find_working_day_all: {e}", exc_info=True)
        return JSONResponse(status_code=500, content={"detail": "Ошибка базы данных"})
    except Exception as e:
        logger.error(f"Unexpected error in find_working_day_all: {e}", exc_info=True)
        return JSONResponse(
            status_code=500, content={"detail": "Внутренняя ошибка сервера"}
        )


@router.post("/add")
async def add_working_day(request: Request, working_day: WorkingDaysInput):
    date_value = None
    admin_id = None
    try:
        if isinstance(working_day, str):
            date_obj = datetime.strptime(working_day, "%Y-%m-%d").date()
        else:
            date_value = working_day.working_day
            date_obj = date_value

        existing_day = await WorkingDayDAO.find_one_or_none(date=date_obj)
        if not existing_day:
            new_day = await WorkingDayDAO.add(date=date_obj)
            if settings.MODE != "TEST":
                try:
                    for admin_id in settings.ADMIN_LIST:
                        await bot.send_message(
                            chat_id=admin_id,
                            text=f"Рабочий день {new_day.date} успешно добавлен!",
                        )

                except Exception as e_bot:
                    logger.error(
                        f"Ошибка при отправке сообщения бота администратору {admin_id}: {e_bot}",
                        exc_info=True,
                    )

            return {"status": "success"}
    except SQLAlchemyError as db_err:
        msg = f"Database Exception work_day {db_err}"
        logger.error(msg, extra={"working_day": date_value}, exc_info=True)
        return JSONResponse(status_code=500, content={"detail": "Ошибка базы данных"})
    except Exception as e:
        msg = f"Unexpected error: {str(e)}"
        logger.error(msg, extra={"working_day": date_value}, exc_info=True)
        return JSONResponse(
            status_code=500, content={"detail": "Внутренняя ошибка сервера"}
        )


@router.get("find_id")
async def find_id_day(working_day: date = Query(...)):
    try:
        working_day_id = await WorkingDayDAO.find_one_or_none(working_day=working_day)
        if not working_day_id:
            return working_day_id
    except SQLAlchemyError as e:
        logger.error(f"Database error in find_id_day: {e}", exc_info=True)
    except Exception as e:
        logger.error(f"Unexpected error in find_id_day: {e}", exc_info=True)


@router.delete("/remove")
async def remove_working_day_data(working_day: date = Query(...)):
    try:
        application_in_works_day = await ApplicationDAO.find_all_applications(
            appointment_date=working_day
        )
        if not application_in_works_day:
            working_day_record = await WorkingDayDAO.find_one_or_none(date=working_day)
            if not working_day_record:
                return JSONResponse(
                    status_code=404, content={"detail": "Рабочий день не найден"}
                )

            await WorkingDayDAO.delete(id=working_day_record.id)
            return {"status": "deleted"}
        else:
            message = f"на {working_day} день есть записи:"
            for application in application_in_works_day:
                message += f"\n{application.client_name} - {application.appointment_time.strftime('%H:%M')} "  # f"(телефон-{application.user.telephone_number})"
            message += "\n удаление не возможно"
            # await bot.send_message(settings.ADMIN_ID, message)
            # Вместо raise JSONResponse
            return JSONResponse(status_code=409, content={"detail": message})

    except SQLAlchemyError as db_err:
        logger.error(
            f"Database error during delete of {working_day}: {db_err}", exc_info=True
        )
        return JSONResponse(status_code=500, content={"detail": "Ошибка базы данных"})
    except Exception as e:
        logger.error(
            f"Unexpected error during delete of {working_day}: {e}", exc_info=True
        )
        return JSONResponse(
            status_code=500, content={"detail": "Внутренняя ошибка сервера"}
        )
