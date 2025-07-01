from typing import Text

from aiogram import Router, F, types
from aiogram.enums import ContentType
from aiogram.filters import CommandStart, StateFilter
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext

from app.api.users.dao import UsersDAO
from app.api.users.dependencies import login_via_telegram
from app.api.users.models import SuperUsers
from app.api.users.router import register_user
from app.bot.keyboards.kbs import app_keyboard
from app.bot.utils.utils import greet_user, get_about_us_text, user_has_phone
from app.config import settings

user_router = Router()

from aiogram.fsm.state import State, StatesGroup


class UserStates(StatesGroup):
    waiting_for_contact = State()


@user_router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    user = await UsersDAO.find_one_or_none(telegram_id=message.from_user.id)
    await state.clear()
    if not user:
        token = None
        if settings.ADMIN_ID == message.from_user.id:
            token = await login_via_telegram(telegram_id=message.from_user.id)
        # Добавляем пользователя
        await UsersDAO.add(
            telegram_id=message.from_user.id,
            first_name=message.from_user.first_name,
            username=message.from_user.username,
            telephone_number=None,
            token=token)

    has_phone = await user_has_phone(message.from_user.id)
    await greet_user(message, is_new_user=False, has_phone=has_phone)


async def send_contact_keyboard(message: Message):
    print("Отправляем клавиатуру для обмена контактом")
    keyboard = ReplyKeyboardMarkup(
        resize_keyboard=False,
        one_time_keyboard=True,
        keyboard=[
            [KeyboardButton(text="Поделиться номером", request_contact=True)]
        ]
    )
    await message.answer("Пожалуйста, поделитесь своим номером", reply_markup=keyboard)


@user_router.message(F.content_type.in_([ContentType.CONTACT]))
async def handle_contact(message: Message, state: FSMContext):
    await state.set_state(UserStates.waiting_for_contact)
    current_state = await state.get_state()
    if current_state == UserStates.waiting_for_contact:
        print("Обработчик контакта вызван")
        contact = message.contact
        if contact:
            print(f"Получен контакт: {contact}")
            phone_number = contact.phone_number
            print(f"Номер телефона: {phone_number}")

            await UsersDAO.update(
                {'telegram_id': message.from_user.id},
                telephone_number=phone_number
            )

            await message.answer("Спасибо! Ваш номер сохранен.", reply_markup=types.ReplyKeyboardRemove())
            await greet_user(message, is_new_user=False, has_phone=True)

    if current_state == UserStates.waiting_for_contact:
        pass
    else:
        print("Контакт не получен")


@user_router.message(F.text == '🔙 Назад')
async def cmd_back_home(message: Message) -> None:
    """
    Обрабатывает нажатие кнопки "Назад".
    """
    await greet_user(message, is_new_user=False, has_phone=True)


@user_router.message(F.text == "ℹ️ О нас")
async def about_us(message: Message):
    kb = app_keyboard(user_id=message.from_user.id, first_name=message.from_user.first_name)
    await message.answer(get_about_us_text(), reply_markup=kb)
