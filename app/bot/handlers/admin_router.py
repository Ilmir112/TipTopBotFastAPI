from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)

from app.api.service.dao import ServiceDAO
from app.api.users.router import read_users_all
from app.bot.keyboards.kbs import admin_keyboard, main_keyboard
from app.config import settings
from app.pages.router import find_all_service


class NewsStates(StatesGroup):
    waiting_for_news = State()


admin_router = Router()


@admin_router.message(
    F.text == "🔑 Админ панель", F.from_user.id.in_(settings.ADMIN_LIST)
)
async def admin_panel(message: Message):
    await message.answer(
        f"Здравствуйте, <b>{message.from_user.full_name}</b>!\n\n"
        "Добро пожаловать в панель администратора. Здесь вы можете:\n"
        "• Просматривать все текущие заявки\n"
        "• Управлять статусами заявок\n"
        "• Анализировать статистику\n\n"
        "Для доступа к полному функционалу, пожалуйста, перейдите по ссылке ниже.",
        reply_markup=await admin_keyboard(user_id=message.from_user.id),
    )


@admin_router.callback_query(F.data == "back_home")
async def cmd_back_home_admin(callback: CallbackQuery):
    await callback.answer(f"С возвращением, {callback.from_user.full_name}!")
    await callback.message.answer(
        f"С возвращением, <b>{callback.from_user.full_name}</b>!\n\n"
        "Надеемся, что работа в панели администратора была продуктивной. "
        "Если у вас есть предложения по улучшению функционала, "
        "пожалуйста, сообщите нам.\n\n"
        "Чем еще я могу помочь вам сегодня?",
        reply_markup=main_keyboard(
            user_id=callback.from_user.id,
            first_name=callback.from_user.first_name,
            has_phone=True,
        ),
    )


@admin_router.callback_query(F.data == "edit_services")
async def handle_edit_application(callback_query: CallbackQuery):
    services = await find_all_service()  # Возвращает список Application

    if not services:
        await callback_query.message.answer("Нет услуг для редактирования.")
        return

    kb = []

    for app in services:
        label = f"{app.service_id} {app.service_name} {app.time_work}"
        # Используем InlineKeyboardButton с callback_data
        kb.append(
            [
                InlineKeyboardButton(
                    text=label, callback_data=f"service_{app.service_id}"
                )
            ]
        )

    # Добавляем кнопку назад
    kb.append([InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_admin")])

    keyboard = InlineKeyboardMarkup(inline_keyboard=kb)

    await callback_query.message.answer(
        "Выберите услугу для редактирования:", reply_markup=keyboard
    )


@admin_router.callback_query(F.data.startswith("service_"))
async def handle_service_selection(callback_query: CallbackQuery):
    service_id = callback_query.data.split("_")[1]

    # Показываем меню с действиями
    kb = [
        [
            InlineKeyboardButton(
                text="Редактировать", callback_data=f"edit_{service_id}"
            ),
            InlineKeyboardButton(text="Удалить", callback_data=f"delete_{service_id}"),
        ],
        [InlineKeyboardButton(text="Назад", callback_data="back_to_services")],
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=kb)

    await callback_query.message.answer(
        f"Что хотите сделать с услугой {service_id}?", reply_markup=keyboard
    )


@admin_router.callback_query(F.data.startswith("edit_"))
async def handle_edit_service(callback_query: CallbackQuery):
    service_id = callback_query.data.split("_")[1]
    # Получите текущие данные услуги из базы
    service = await ServiceDAO.find_one_or_none_by_id(service_id=service_id)
    # Отправьте сообщение с формой или запросом новых данных
    await callback_query.message.answer(
        f"Редактирование услуги {service.service_name}.\nВведите новое название:"
    )
    # Можно сохранить состояние для следующего шага (например, через FSM)


@admin_router.callback_query(F.data.startswith("delete_"))
async def handle_delete_service(callback_query: CallbackQuery):
    service_id = callback_query.data.split("_")[1]
    # Удалите услугу из базы
    success = await ServiceDAO.delete(service_id=int(service_id))
    if success:
        await callback_query.message.answer("Услуга успешно удалена.")
    else:
        await callback_query.message.answer("Ошибка при удалении услуги.")


@admin_router.callback_query(F.data == "add_news")
async def handle_add_news(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer(
        "Пожалуйста, введите текст новости, которую хотите "
        "отправить всем пользователям."
    )

    await callback.answer()

    # Предположим, что у вас есть состояние 'waiting_for_news'
    await state.set_state(NewsStates.waiting_for_news)


# Обработчик текста при ожидании новости
@admin_router.message(NewsStates.waiting_for_news)
async def process_news_message(message: Message, state: FSMContext):
    news_text = message.text

    # Получить список всех пользователей из базы данных
    users = await read_users_all()  # Реализуйте эту функцию

    for user_id in users:
        try:
            await message.bot.send_message(user_id.telegram_id, news_text)
        except Exception as e:
            # Логировать ошибку или пропустить
            print(f"Ошибка при отправке пользователю {user_id.first_name}: {e}")

    await message.answer("Новость успешно отправлена всем пользователям.")

    # Сброс состояния
    await state.clear()
