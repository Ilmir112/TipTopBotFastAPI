import asyncio
from datetime import datetime, timedelta, time
import pytz

from app.api.applications.router import get_applications_all
from app.bot.create_bot import bot


async def send_reminders():
    # Часовой пояс Екатеринбурга
    ekaterinburg_tz = pytz.timezone('Asia/Yekaterinburg')

    # Получить текущее время в Екатеринбурге
    now = datetime.now(ekaterinburg_tz)

    # Получаем все заявки
    applications = await get_applications_all()

    for app in applications:
        # Проверяем условия для напоминания
        appointment_datetime = datetime.combine(app.appointment_date, app.appointment_time)
        # Актуализируем его в нужный часовой пояс
        appointment_datetime = ekaterinburg_tz.localize(appointment_datetime)

        delta = appointment_datetime - now

        # Напоминание за 24 часа
        if timedelta(hours=23, minutes=00) < delta <= timedelta(hours=24, minutes=30):
            user_id = app.user_id
            message = (f"🔔✨ Напоминание: у вас запланирована запись на услугу {app.service} 🛎️\n"
                       f"📅 Дата: {app.appointment_date} 🗓️\n"
                       f"🕒 Время: {app.appointment_time.strftime('%H:%M')}. ⏰")
            await bot.send_message(user_id, message)

        # Напоминание в 8 утра в день записи
        if app.appointment_date == now.date():
            # Проверяем время сейчас и время записи
            now_time = datetime.now(ekaterinburg_tz).time()
            if now_time >= time(7, 59) and now_time <= time(8, 10):  # например, в первые минуты после 8 утра
                user_id = app.user_id
                message = (f"🌅 Доброе утро! ☀️ Напоминаем о вашей записи сегодня "
                           f"в {app.appointment_time.strftime('%H:%M')}📅🕒 на услугу {app.service} 🛎️")
                await bot.send_message(user_id, message)
