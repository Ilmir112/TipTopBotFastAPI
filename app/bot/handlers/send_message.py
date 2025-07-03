import asyncio
from datetime import datetime, timedelta, time


from app.api.applications.router import get_applications_all
from app.bot.create_bot import bot


async def send_reminders():
    now = datetime.utcnow()
    # Получаем все заявки
    applications = await get_applications_all()

    for app in applications:
        # Проверяем условия для напоминания
        appointment_datetime = datetime.combine(app.appointment_date, app.appointment_time)
        delta = appointment_datetime - now

        # Напоминание за 24 часа
        if timedelta(hours=23, minutes=59) < delta <= timedelta(hours=24):
            user_id = app.user_id
            message = f"Напоминание: у вас запланирована запись на {app.appointment_date} в {app.appointment_time}."
            await bot.send_message(user_id, message)

        # Напоминание в 8 утра в день записи
        if app.appointment_date == now.date():
            # Проверяем время сейчас и время записи
            asddd = now.time()
            if now.time() >= time(10, 15) and now.time() <= time(10, 20):  # например, в первые минуты после 8 утра
                user_id = app.user_id
                message = f"Доброе утро! Напоминаем о вашей записи сегодня в {app.appointment_time}."
                await bot.send_message(user_id, message)