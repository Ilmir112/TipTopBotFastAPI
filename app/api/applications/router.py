from datetime import date, datetime

from fastapi import APIRouter, Depends
from fastapi.requests import Request
from fastapi.responses import JSONResponse
from app.api.applications.schemas import AppointmentData
from app.bot.create_bot import bot
from app.api.applications.dao import ApplicationDAO
from app.bot.handlers.user_router import check_admin
from app.bot.keyboards.kbs import main_keyboard, applications_list_keyboard
from app.config import settings
from app.logger import logger

router = APIRouter(prefix='/api', tags=['API'])


@router.get('/get_booked_times')
async def get_booked_times(appointment_date: date):
    time_list = ['09:00', '09:30', '10:00', '10:30', '11:00', '11:30', '12:00',
                 '12:30', "13:00", "13:30", "14:00", "14:30", "15:00", "15:30",
                 "16:00", "16:30", "17:00", "17:30"]
    result = await ApplicationDAO.get_booked_times(appointment_date)
    if result:
        result_strs = [t.strftime("%H:%M") for t in result]
        new_time_list = []
        for time in time_list:
            if any([time in result_strs]) is False:
                new_time_list.append(time)

        return new_time_list
    return time_list

@router.get('/find_applications')
async def get_applications_all():
    applications_list = await ApplicationDAO.find_all()
    return applications_list


@router.post('/add')
async def add_appointment(data: AppointmentData):
    return ApplicationDAO.add(
        name=data.name,
        service=int(data.service),
        appointment_date=data.appointment_date,
        appointment_time=data.appointment_time,
        user_id=data.user_id)


@router.post("/appointment", response_class=JSONResponse)
async def create_appointment(request: Request):
    # Получаем и валидируем JSON данные
    data = await request.json()

    validated_data = AppointmentData(**data)

    # master_id, master_name = validated_data.master.split('_')
    service_id, service_name = validated_data.service.split('_')

    # Добавление заявки в базу данных
    result = await ApplicationDAO.add_appointment_if_available(
        user_id=validated_data.user_id,
        # master_id=int(master_id),
        service_id=int(service_id),
        appointment_date=validated_data.appointment_date,
        appointment_time=validated_data.appointment_time,
        client_name=validated_data.name
    )

    # Формируем сообщение для пользователя
    message = (
        f"🎉 <b>{validated_data.name}, ваша заявка успешно принята!</b>\n\n"
        "💬 <b>Информация о вашей записи:</b>\n"
        f"👤 <b>Имя клиента:</b> {validated_data.name}\n"
        f"💇 <b>Услуга:</b> {service_name}\n"
        # f"✂️ <b>Мастер:</b> {master_name}\n"
        f"📅 <b>Дата записи:</b> {validated_data.appointment_date}\n"
        f"⏰ <b>Время записи:</b> {validated_data.appointment_time}\n\n"
        "Спасибо за выбор нашего шиномонтажа! ✨ Мы ждём вас в назначенное время."
    )

    # Сообщение администратору
    admin_message = (
        "🔔 <b>Новая запись!</b>\n\n"
        "📄 <b>Детали заявки:</b>\n"
        f"👤 Имя клиента: {validated_data.name}\n"
        f"💇 Услуга: {service_name}\n"
        # f"✂️ Мастер: {master_name}\n"
        f"📅 Дата: {validated_data.appointment_date}\n"
        f"⏰ Время: {validated_data.appointment_time}"

    )

    if validated_data.user_id:
        kb = main_keyboard(user_id=validated_data.user_id, first_name=validated_data.name, has_phone=True)
    # Отправка сообщений через бота
    if result:
        if validated_data.user_id:
            await bot.send_message(chat_id=validated_data.user_id, text=message, reply_markup=kb)
        if check_admin(validated_data.user_id):
            await bot.send_message(chat_id=check_admin(validated_data.user_id), text=admin_message, reply_markup=kb)
        # Возвращаем успешный ответ
        return {"status": "success", "message": "Заявка успешно создана"}
    else:
        message = (
            f"🎉 <b>{validated_data.name}, "
            f"⏰ <b>Время записи:</b> {validated_data.appointment_time} Занято \n\n"
            "Прошу выбрать другое время."
        )
        if validated_data.user_id:
            await bot.send_message(chat_id=validated_data.user_id, text=message, reply_markup=kb)
        # Возвращаем успешный ответ
        return {"status": "busy", "message": "Время занято"}


@router.delete("/delete", response_class=JSONResponse)
async def delete_application(request: Request, application_id: int):
    result = await ApplicationDAO.find_one_or_none(id=application_id)

    if result:
        await ApplicationDAO.delete(id=application_id)

        # Формируем сообщение для пользователя
        message = (
            f"🎉 <b>{result.client_name}, ваша заявка успешно удалена!</b>\n\n"
            "💬 <b>Информация о вашей записи:</b>\n"
            f"👤 <b>Имя клиента:</b> {result.client_name}\n"
            # f"✂️ <b>Мастер:</b> {master_name}\n"
            f"📅 <b>Дата записи:</b> {result.appointment_date}\n"
            f"⏰ <b>Время записи:</b> {result.appointment_time}\n\n"
            "Спасибо за выбор нашего шиномонтажа! ✨ Мы ждём вас в назначенное время."
        )

        # Сообщение администратору
        admin_message = (
            "🔔 <b>запись удалена!</b>\n\n"
            "📄 <b>Детали заявки:</b>\n"
            f"👤 Имя клиента: {result.client_name}\n"
            # f"✂️ Мастер: {master_name}\n"
            f"📅 Дата: {result.appointment_date}\n"
            f"⏰ Время: {result.appointment_time}"

        )

        kb = main_keyboard(user_id=result.user_id, first_name=result.client_name, has_phone=True)
        # Отправка сообщений через бота
        if result:
            try:
                await bot.send_message(chat_id=result.user_id, text=message, reply_markup=kb)
            except Exception as e:
                logger.error(e)
            for admin_id in settings.ADMIN_LIST:
                await bot.send_message(chat_id=admin_id, text=admin_message, reply_markup=kb)
            # Возвращаем успешный ответ
            return {"status": "success", "message": "Заявка успешно удалена"}

        return {"status": "success"}
    return {"status": "fail"}
