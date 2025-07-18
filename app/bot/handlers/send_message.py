import asyncio
from datetime import datetime, time, timedelta

import pytz

from app.api.applications.router import get_applications_all
from app.bot.create_bot import bot


async def send_reminders():
    # Часовой пояс Екатеринбурга
    ekaterinburg_tz = pytz.timezone("Asia/Yekaterinburg")

    # Получить текущее время в Екатеринбурге
    now = datetime.now(ekaterinburg_tz)

    # Получаем все заявки с предварительной загрузкой связанного service
    applications = (
        await get_applications_all()
    )  # Предполагается, что внутри этой функции используется joinedload для app.service

    # Получить текущее время для сравнения (чтобы не вызывать много раз)
    now_time = datetime.now(ekaterinburg_tz).time()
    if applications:
        for app in applications:
            # Объединяем дату и время записи
            appointment_datetime = datetime.combine(
                app.appointment_date, app.appointment_time
            )
            appointment_datetime = ekaterinburg_tz.localize(appointment_datetime)

            delta = appointment_datetime - now

            # Напоминание за 24 часа (примерно)
            if (
                timedelta(hours=23, minutes=31)
                <= delta
                <= timedelta(hours=24, minutes=30)
            ):
                user_id = app.user_id
                message = (
                    f"🔔✨ Напоминание: у вас запланирована запись "
                    f"в шиномонтаж TIP-TOP на завтра"
                    f"на услугу {app.service.service_name} 🛎️\n "
                    f"📅 Дата: {app.appointment_date.strftime('%d.%m.%Y')} 🗓️\n"
                    f"🕒 Время: {app.appointment_time.strftime('%H:%M')}. ⏰"
                )
                await bot.send_message(user_id, message)

            # Напоминание в 8 утра в день записи
            if app.appointment_date == now.date():
                # Проверяем время сейчас — примерно между 07:59 и 08:10
                if time(7, 20) <= now_time <= time(8, 20):
                    user_id = app.user_id
                    message = (
                        f"🌅 Доброе утро! ☀️ Напоминаем о вашей записи сегодня в шиномонтаж TIP-TOP"
                        f"в {app.appointment_time.strftime('%H:%M')} 📅🕒 на услугу {app.service.service_name} 🛎️"
                    )
                    await bot.send_message(user_id, message)
