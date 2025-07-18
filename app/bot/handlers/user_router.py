from aiogram import F, Router, types
from aiogram.enums import ContentType
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from app.api.users.dao import UsersDAO
from app.api.users.dependencies import login_via_telegram
from app.bot.keyboards.kbs import app_keyboard
from app.bot.utils.utils import get_about_us_text, greet_user
from app.config import settings

user_router = Router()

from aiogram.fsm.state import State, StatesGroup


class UserStates(StatesGroup):
    waiting_for_contact = State()


def check_admin(user_id: int):
    return user_id if user_id in settings.ADMIN_LIST else None


@user_router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    settings.ADMIN_ID = check_admin(message.from_user.id)
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
            token=token,
        )

        await greet_user(message, is_new_user=True, has_phone=False)
    else:
        await greet_user(message, is_new_user=False, has_phone=False)


@user_router.message(F.content_type.in_([ContentType.CONTACT]))
async def handle_contact(message: Message, state: FSMContext):
    await state.set_state(UserStates.waiting_for_contact)
    current_state = await state.get_state()
    if current_state == UserStates.waiting_for_contact:
        contact = message.contact
        if contact:
            phone_number = contact.phone_number
            # Обновляем номер телефона в базе данных
            await UsersDAO.update(
                {"telegram_id": message.from_user.id}, telephone_number=phone_number
            )
            # Удаляем клавиатуру после получения контакта
            await message.answer(
                "Спасибо! Ваш номер сохранен.", reply_markup=types.ReplyKeyboardRemove()
            )
            # Продолжаем взаимодействие (например, приветствие или переход к следующему шагу)
            await greet_user(message, is_new_user=False, has_phone=True)
            # После этого можно снова показать основную клавиатуру или выполнить другие действия


@user_router.message(F.text == "🔙 Назад")
async def cmd_back_home(message: Message) -> None:
    """
    Обрабатывает нажатие кнопки "Назад".
    """
    await greet_user(message, is_new_user=False, has_phone=True)


@user_router.message(F.text == "ℹ️ О нас")
async def about_us(message: Message):
    kb = app_keyboard(
        user_id=message.from_user.id, first_name=message.from_user.first_name
    )
    await message.answer(get_about_us_text(), reply_markup=kb)
