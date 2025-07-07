from datetime import date

from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse
from app.api.applications.schemas import AppointmentData
from app.api.service.dao import ServiceDAO
from app.bot.create_bot import bot
from app.api.applications.dao import ApplicationDAO
from app.bot.handlers.user_router import check_admin
from app.bot.keyboards.kbs import main_keyboard
from app.config import settings
from app.logger import logger

router = APIRouter(prefix='/api', tags=['API'])


@router.get('/get_booked_times')
async def get_booked_times(appointment_date: date):
    time_list = ['09:00', '09:30', '10:00', '10:30', '11:00', '11:30', '12:00',
                 '12:30', "13:00", "13:30", "14:00", "14:30", "15:00", "15:30",
                 "16:00", "16:30", "17:00", "17:30"]
    try:
        result = await ApplicationDAO.get_booked_times(appointment_date)
        if result:
            result_strs = [t.strftime("%H:%M") for t in result]
            new_time_list = [time for time in time_list if not any(time == t for t in result_strs)]
            return new_time_list
        return time_list
    except Exception as e:
        logger.error(f"Error fetching booked times for {appointment_date}: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.get('/find_applications')
async def get_applications_all():
    try:
        applications_list = await ApplicationDAO.find_all()
        return applications_list
    except Exception as e:
        logger.error(f"Error fetching applications: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.post('/add')
async def add_appointment(data: AppointmentData):
    try:
        service = await ServiceDAO.find_all(service_name=data.service_name)
        if service:
            return await ApplicationDAO.add(
                client_name=data.name,
                service_id=service.service_id,
                appointment_date=data.appointment_date,
                appointment_time=data.appointment_time,
                user_id=data.user_id)
        else:
            raise HTTPException(status_code=404, detail="Service not found")
    except Exception as e:
        logger.error(f"Error adding appointment: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")



@router.post("/appointment", response_class=JSONResponse)
async def create_appointment(request: Request):
    try:
        data = await request.json()
    except Exception as e:
        logger.error(f"Error parsing JSON request body: {e}")
        raise HTTPException(status_code=400, detail="Invalid JSON payload")

    try:
        validated_data = AppointmentData(**data)
    except Exception as e:
        logger.error(f"Validation error for data {data}: {e}")
        raise HTTPException(status_code=422, detail="Validation error")

    try:
        service_id_str, service_name = validated_data.service.split('_')
    except Exception as e:
        logger.error(f"Error parsing service field '{validated_data.service}': {e}")
        raise HTTPException(status_code=400, detail="Invalid service format")

    try:
        result = await ApplicationDAO.add_appointment_if_available(
            user_id=validated_data.user_id,
            service_id=int(service_id_str),
            appointment_date=validated_data.appointment_date,
            appointment_time=validated_data.appointment_time,
            client_name=validated_data.name
        )
    except Exception as e:
        logger.error(f"Error adding appointment if available: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

    # Формируем сообщение для пользователя и администратора
    message = (
        f"🎉 <b>{validated_data.name}, ваша заявка успешно принята!</b>\n\n"
        "💬 <b>Информация о вашей записи:</b>\n"
        f"👤 <b>Имя клиента:</b> {validated_data.name}\n"
        f"💇 <b>Услуга:</b> {service_name}\n"
        f"📅 <b>Дата записи:</b> {validated_data.appointment_date}\n"
        f"⏰ <b>Время записи:</b> {validated_data.appointment_time}\n\n"
        "Спасибо за выбор нашего шиномонтажа! ✨ Мы ждём вас в назначенное время."
    )

    admin_message = (
        "🔔 <b>Новая запись!</b>\n\n"
        "📄 <b>Детали заявки:</b>\n"
        f"👤 Имя клиента: {validated_data.name}\n"
        f"💇 Услуга: {service_name}\n"
        f"📅 Дата: {validated_data.appointment_date}\n"
        f"⏰ Время: {validated_data.appointment_time}"
    )

    # Отправка сообщений через бота с обработкой ошибок
    try:
        if validated_data.user_id:
            kb = main_keyboard(user_id=validated_data.user_id, first_name=validated_data.name, has_phone=True)
            await bot.send_message(chat_id=validated_data.user_id, text=message, reply_markup=kb)

            if check_admin(validated_data.user_id):
                admin_chat_id = check_admin(validated_data.user_id)
                await bot.send_message(chat_id=admin_chat_id, text=admin_message, reply_markup=kb)
    except Exception as e:
        logger.error(f"Error sending messages via bot or creating keyboard: {e}")

    if result:
        return {"status": "success", "message": "Заявка успешно создана"}
    else:
        # В случае если результат не получен (например время занято), возвращаем соответствующий статус
        message_busy = (
            f"🎉 <b>{validated_data.name}, "
            f"⏰ <b>Время записи:</b> {validated_data.appointment_time} Занято \n\n"
            "Прошу выбрать другое время."
        )

        try:
            if validated_data.user_id:
                kb = main_keyboard(user_id=validated_data.user_id, first_name=validated_data.name, has_phone=True)
                await bot.send_message(chat_id=validated_data.user_id, text=message_busy, reply_markup=kb)
        except Exception as e:
            logger.error(f"Error sending busy time message via bot: {e}")

        return {"status": "busy", "message": "Время занято"}


@router.delete("/delete", response_class=JSONResponse)
async def delete_application(request: Request, application_id: int):
    try:
        result = await ApplicationDAO.find_one_or_none(id=application_id)

        if not result:
            raise HTTPException(status_code=404, detail="Application not found")

        await ApplicationDAO.delete(id=application_id)

    except HTTPException as he:
        # Перебрасываем исключение дальше без логирования как ошибку сервера
        raise he
    except Exception as e:
        logger.error(f"Error deleting application with id={application_id}: {e}")

    # После успешного удаления формируем сообщения и отправляем их
    try:

        # Формируем сообщение для пользователя
        message_user = (
            f"🎉 <b>{result.client_name}, ваша заявка успешно удалена!</b>\n\n"
            "💬 <b>Информация о вашей записи:</b>\n"
            f"👤 <b>Имя клиента:</b> {result.client_name}\n"
            f"📅 <b>Дата записи:</b> {result.appointment_date}\n"
            f"⏰ <b>Время записи:</b> {result.appointment_time}\n\n"
            "Спасибо за выбор нашего шиномонтажа! ✨ Мы ждём вас в назначенное время."
        )

        # Сообщение администратору
        admin_message = (
            "🔔 <b>запись удалена!</b>\n\n"
            "📄 <b>Детали заявки:</b>\n"
            f"👤 Имя клиента: {result.client_name}\n"
            f"📅 Дата: {result.appointment_date}\n"
            f"⏰ Время: {result.appointment_time}"
        )

        kb = main_keyboard(user_id=result.user_id, first_name=result.client_name, has_phone=True)

        # Отправка сообщений через бота с обработкой ошибок
        try:
            await bot.send_message(chat_id=result.user_id, text=message_user, reply_markup=kb)
        except Exception as e:
            logger.error(f"Error sending message to user ID={result.user_id}: {e}")

        for admin_id in settings.ADMIN_LIST or []:
            try:
                await bot.send_message(chat_id=admin_id, text=admin_message)
            except Exception as e:
                logger.error(f"Error sending message to admin ID={admin_id}: {e}")

        return {"status": "success", "message": "Заявка успешно удалена"}

    except Exception as e:
        logger.error(f"Unexpected error during deletion process for application ID={application_id}: {e}")
        return {"status": "fail"}
