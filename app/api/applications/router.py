from datetime import date, datetime

from fastapi import APIRouter, Depends
from fastapi.requests import Request
from fastapi.responses import JSONResponse
from app.api.applications.schemas import AppointmentData
from app.bot.create_bot import bot
from app.api.applications.dao import ApplicationDAO
from app.bot.keyboards.kbs import main_keyboard
from app.config import settings

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


    kb = main_keyboard(user_id=validated_data.user_id, first_name=validated_data.name, has_phone=True)
    # Отправка сообщений через бота
    if result:
        await bot.send_message(chat_id=validated_data.user_id, text=message, reply_markup=kb)
        await bot.send_message(chat_id=settings.ADMIN_ID, text=admin_message, reply_markup=kb)
        # Возвращаем успешный ответ
        return {"message": "success!"}
    else:
        message = (
            f"🎉 <b>{validated_data.name}, "
            f"⏰ <b>Время записи:</b> {validated_data.appointment_time} Занято \n\n"
            "Прошу выбрать другое время."
        )
        await bot.send_message(chat_id=validated_data.user_id, text=message, reply_markup=kb)
        # Возвращаем успешный ответ
        return {"message": "busy"}


