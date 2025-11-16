import re
from datetime import datetime

from aiogram import types
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

from app.api.applications.dao import ApplicationDAO
from app.api.applications.router import get_booked_times
from app.api.service.router import find_service_all
from app.api.users.dao import UsersDAO
from app.api.users.router import register_user
from app.api.users.schemas import SUsers
from app.api.working_day.dao import WorkingDayDAO

from app.bot.create_bot import bot
from app.bot.handlers.user_router import user_router
from app.config import settings


class BookingStates(StatesGroup):
    waiting_for_name = State()
    waiting_for_telephone_number = State()
    waiting_for_service = State()
    waiting_for_date = State()
    waiting_for_time = State()


# Кнопка для начала создания заявки (если нужно)
create_admin_application_button = InlineKeyboardButton(
    text="👨‍🦱 Создать заявку для пользователя",
    callback_data="start_create_application",
)


@user_router.callback_query(lambda c: c.data == "start_create_application")
async def start_booking(callback: types.CallbackQuery, state: FSMContext):
    # Начинаем с ожидания имени клиента
    await callback.message.answer("Пожалуйста, введите номер телефона:")
    await state.set_state(BookingStates.waiting_for_telephone_number)


# Валидация номера телефона (пример)
def validate_phone_number(phone: str) -> bool:
    pattern = r"^\+?\d{10,15}$"  # пример: +1234567890 или 1234567890
    return re.match(pattern, phone.strip()) is not None


@user_router.message(StateFilter(BookingStates.waiting_for_telephone_number))
async def process_name(message: Message, state: FSMContext):
    phone = message.text.strip()

    # Проверка валидности номера телефона
    if not validate_phone_number(phone):
        await message.answer(
            "Некорректный формат номера телефона. Пожалуйста, введите корректный номер:"
        )
        return  # остаться в этом же состоянии

    # Проверка наличия номера в базе
    user = await UsersDAO.find_one_or_none(telephone_number=phone)
    if user:
        await state.update_data(telephone_number=phone)
        await state.update_data(user_id=user.telegram_id)
        await state.update_data(name=user.first_name)
        await message.answer("Пользователь найден. Переходим к выбору услуги.")

        # Получить список услуг и показать их
        services = await find_service_all()
        buttons = [
            InlineKeyboardButton(
                text=service.service_name, callback_data=f"service_{service.service_id}"
            )
            for service in services
        ]
        rows = [buttons[i : i + 4] for i in range(0, len(buttons), 4)]
        keyboard = InlineKeyboardMarkup(inline_keyboard=rows)
        await message.answer("Пожалуйста, выберите услугу:", reply_markup=keyboard)
        await state.set_state(BookingStates.waiting_for_service)
    else:
        # Сохраняем имя клиента и запрашиваем номер телефона
        await state.update_data(telephone_number=message.text)
        await message.answer("Введите имя клиента")
        await state.set_state(BookingStates.waiting_for_name)


@user_router.message(StateFilter(BookingStates.waiting_for_name))
async def process_telephone_number(message: Message, state: FSMContext):
    # Сохраняем номер телефона и запрашиваем услугу
    await state.update_data(name=message.text)
    name = message.text
    user_data = await state.get_data()

    telephone_number = user_data.get("telephone_number")

    new_user_data = SUsers(
        first_name=name, username=telephone_number, telephone_number=telephone_number
    )

    new_user = await register_user(new_user_data)
    if new_user is None:
        return
    user_id = new_user.telegram_id
    await state.update_data(user_id=user_id)

    # Запросить услугу через inline клавиатуру
    services = await find_service_all()

    buttons = [
        InlineKeyboardButton(
            text=service.service_name, callback_data=f"service_{service.service_id}"
        )
        for service in services
    ]

    # Группируем по 4 кнопки в строку
    rows = [buttons[i : i + 4] for i in range(0, len(buttons), 4)]

    # Создаем клавиатуру
    keyboard = InlineKeyboardMarkup(inline_keyboard=rows)
    await message.answer("Пожалуйста, выберите услугу:", reply_markup=keyboard)
    await state.set_state(BookingStates.waiting_for_name)


@user_router.callback_query(lambda c: c.data.startswith("service_"))
async def service_chosen(callback_query: types.CallbackQuery, state: FSMContext):
    data = callback_query.data
    if data.startswith("service_"):
        service = int(data.split("_")[1])
        await state.update_data(service_id=service)

        # Запросить даты
        dates = await WorkingDayDAO.find_all(start_date=date.today())

        # Преобразовать даты в строки
        date_strings = [
            date.strftime("%d.%m.%Y")
            for date in sorted(dates)
            if date >= datetime.now().date()
        ]

        # Создаем список списков кнопок
        buttons = [
            InlineKeyboardButton(text=date_str, callback_data=f"date_{date_str}")
            for date_str in date_strings
        ]

        # Группируем по 4 кнопки в строку
        rows = [buttons[i : i + 3] for i in range(0, len(buttons), 3)]

        # Создаем клавиатуру из списка списков словарей
        keyboard = InlineKeyboardMarkup(inline_keyboard=rows)

        await callback_query.message.edit_text("Выберите дату:", reply_markup=keyboard)
        await state.set_state(BookingStates.waiting_for_date)


@user_router.callback_query(lambda c: c.data.startswith("date_"))
async def date_chosen(callback_query: types.CallbackQuery, state: FSMContext):
    data = callback_query.data
    if data.startswith("date_"):
        date_str = data.split("_")[1]
        appointment_date = datetime.strptime(date_str, "%d.%m.%Y")
        await state.update_data(appointment_date=appointment_date)

        # Получить занятые времена на выбранную дату
        booked_times = await get_booked_times(
            appointment_date
        )  # вызов API /get_booked_times

        buttons = [
            InlineKeyboardButton(text=time_str, callback_data=f"time_{time_str}")
            for time_str in booked_times
        ]

        # Группируем по 4 кнопки в строку
        rows = [buttons[i : i + 4] for i in range(0, len(buttons), 4)]

        # Создаем клавиатуру
        keyboard = InlineKeyboardMarkup(inline_keyboard=rows)

        await callback_query.message.edit_text("Выберите время:", reply_markup=keyboard)
        await state.set_state(BookingStates.waiting_for_time)


@user_router.callback_query(lambda c: c.data.startswith("time_"))
async def time_chosen(callback_query: types.CallbackQuery, state: FSMContext):
    data = callback_query.data
    if data.startswith("time_"):
        appointment_time_str = data.split("_")[1]
        appointment_time = datetime.strptime(appointment_time_str, "%H:%M").time()

        user_data = await state.get_data()

        name = user_data.get("name")
        user_id = user_data.get("user_id")

        service_id = user_data.get("service_id")
        appointment_date = user_data.get("appointment_date")

        working_day = await WorkingDayDAO.find_one_or_none(date=appointment_date)
        appointment_date = appointment_date.strftime("%d.%m.%Y")
        success = await ApplicationDAO.add_appointment_if_available(
            client_name=name,
            service_id=service_id,
            appointment_date=datetime.strptime(appointment_date, "%d.%m.%Y").date(),
            appointment_time=appointment_time,
            user_id=user_id,
            working_day_id=working_day.id,
        )

        if success:
            # Отправить подтверждение пользователю и админу
            message = (
                f"🎉 <b>{name}, ваша заявка успешно создана!</b>\n\n"
                "💬 <b>Информация о вашей записи:</b>\n"
                f"👤 <b>Имя клиента:</b> {name}\n"
                # f"✂️ <b>Мастер:</b> {master_name}\n"
                f"📅 <b>Дата записи:</b> {appointment_date}\n"
                f"⏰ <b>Время записи:</b> {appointment_time}\n\n"
                "Спасибо за выбор нашего шиномонтажа!"
                " ✨ Мы ждём вас в назначенное время."
            )

            # Сообщение администратору
            admin_message = (
                "🔔 <b>запись создана!</b>\n\n"
                "📄 <b>Детали заявки:</b>\n"
                f"👤 Имя клиента: {name}\n"
                # f"✂️ Мастер: {master_name}\n"
                f"📅 Дата: {appointment_date}\n"
                f"⏰ Время: {appointment_time}"
            )
            if user_id:
                if user_id > 52565458:
                    await bot.send_message(chat_id=user_id, text=message)
            for admin_id in settings.ADMIN_LIST:
                await bot.send_message(admin_id, text=admin_message)

            await callback_query.message.edit_text("Спасибо! Ваша заявка принята.")
            await state.clear()
        else:
            # Время занято или ошибка — повторный выбор или сообщение об ошибке.
            await callback_query.message.edit_text(
                "Это время уже занято. Пожалуйста, выберите другое."
            )
