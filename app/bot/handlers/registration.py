from aiogram import types
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)

from app.api.users.router import register_super_user
from app.api.users.schemas import SUsersRegister
from app.bot.handlers.admin_router import admin_router


class SuperUserForm(StatesGroup):
    login_user = State()
    name_user = State()
    surname_user = State()
    second_name = State()
    password = State()
    access_level = State()
    telegram_id = State()


# Клавиатура для начала создания суперюзера
create_superuser_button = InlineKeyboardButton(
    text="Создать супер пользователя", callback_data="start_create_superuser"
)


# Обработчик для запуска процесса:
@admin_router.callback_query(lambda c: c.data == "start_create_superuser")
async def handle_start_create_superuser(
    callback: types.CallbackQuery, state: FSMContext
):
    await callback.message.answer("Введите логин пользователя:")
    await state.set_state(SuperUserForm.login_user)


@admin_router.message(StateFilter(SuperUserForm.login_user))
async def process_login_user(message: Message, state: FSMContext):
    await state.update_data(login_user=message.text)
    await state.update_data(telegram_id=message.from_user.id)
    await message.answer("Введите имя пользователя:")
    await state.set_state(SuperUserForm.name_user)


@admin_router.message(StateFilter(SuperUserForm.name_user))
async def process_name_user(message: Message, state: FSMContext):
    await state.update_data(name_user=message.text)
    await message.answer("Введите фамилию пользователя:")
    await state.set_state(SuperUserForm.surname_user)


@admin_router.message(StateFilter(SuperUserForm.surname_user))
async def process_surname_user(message: Message, state: FSMContext):
    await state.update_data(surname_user=message.text)
    await message.answer("Введите отчество пользователя:")
    await state.set_state(SuperUserForm.second_name)


@admin_router.message(StateFilter(SuperUserForm.second_name))
async def process_second_name(message: Message, state: FSMContext):
    await state.update_data(second_name=message.text)
    await message.answer("Введите пароль:")
    await state.set_state(SuperUserForm.password)


@admin_router.message(SuperUserForm.password)
async def process_password(message: Message, state: FSMContext):
    password = message.text
    if password.isdigit():
        # Если пароль состоит только из цифр, попросить повторить ввод
        await message.answer(
            "Пароль не должен состоять только из цифр. Попробуйте еще раз:"
        )
        # Остаемся в том же состоянии для повторного ввода пароля
        await state.set_state(SuperUserForm.password)
    else:
        # Обработка правильного пароля или продолжение логики
        await state.update_data(password=password)

        # Можно добавить выбор уровня доступа или задать фиксированный
        access_level_keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="Админ", callback_data="access_admin")]
            ]
        )

        await message.answer(
            "Выберите уровень доступа:", reply_markup=access_level_keyboard
        )


@admin_router.callback_query(lambda c: c.data.startswith("access_"))
async def process_access_level(callback_query: types.CallbackQuery, state: FSMContext):
    access_level = callback_query.data.split("_")[1]
    data = await state.get_data()
    data["access_level"] = access_level

    # Сохраняем все данные и создаем запись в базе
    new_superuser = SUsersRegister(
        login_user=data["login_user"],
        name_user=data["name_user"],
        surname_user=data["surname_user"],
        second_name=data["second_name"],
        password=data["password"],  # Лучше хэшировать пароль!
        access_level=access_level,
        telegram_id=data["telegram_id"],
    )

    # Сохраняем в базу (предположим, у вас есть сессия SQLAlchemy)
    result = await register_super_user(new_superuser)
    if result:
        await callback_query.message.answer(
            "Суперпользователь успешно создан!", reply_markup=None
        )

    # Завершаем состояние
    await state.clear()
