from aiogram.types import ReplyKeyboardMarkup, WebAppInfo, InlineKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder

from app.config import settings



def main_keyboard(user_id: int, first_name: str, has_phone: bool=False) -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    url_applications = f"{settings.BASE_SITE}/applications?user_id={user_id}"
    url_add_application = f'{settings.BASE_SITE}/form?user_id={user_id}&first_name={first_name}'
    # Проверяем наличие номера телефона
    if not has_phone:
        # Создаем клавиатуру с кнопкой для отправки контакта
        contact_button = KeyboardButton(
            text="Отправить контакт 📞",
            request_contact=True
        )
        kb.row(contact_button)
        return kb.as_markup(resize_keyboard=True)

    kb.button(text="🌐 Мои заявки", web_app=WebAppInfo(url=url_applications))
    kb.button(text="📝 Оставить заявку", web_app=WebAppInfo(url=url_add_application))
    kb.button(text="ℹ️ О нас")
    if user_id == settings.ADMIN_ID:
        kb.button(text="🔑 Админ панель")
    kb.adjust(1)
    return kb.as_markup(resize_keyboard=True)


def back_keyboard() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.button(text="🔙 Назад")
    kb.adjust(1)
    return kb.as_markup(resize_keyboard=True)


def admin_keyboard(user_id: int) -> InlineKeyboardMarkup:
    url_applications = f"{settings.BASE_SITE}/admin_telegram?admin_id={user_id}"
    url_edit_work_days = f'{settings.BASE_SITE}/work_days?user_id={user_id}'
    kb = InlineKeyboardBuilder()
    kb.button(text="🏠 На главную", callback_data="back_home")
    kb.button(text="📝 Смотреть заявки", web_app=WebAppInfo(url=url_applications))
    kb.button(text="⏰ Редактировать рабочие дни",web_app=WebAppInfo(url=url_edit_work_days))
    kb.adjust(1)
    return kb.as_markup()



def app_keyboard(user_id: int, first_name: str) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    url_add_application = f'{settings.BASE_SITE}/form?user_id={user_id}&first_name={first_name}'
    kb.button(text="📝 Оставить заявку", web_app=WebAppInfo(url=url_add_application))
    kb.adjust(1)
    return kb.as_markup()

def applications_list_keyboard(applications: list["Application"]) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for app in applications:
        # Можно отображать дату и имя клиента
        label = f"{app.appointment_date} {app.client_name}"
        callback_data = f"edit_application:{app.id}"
        kb.button(text=label, callback_data=callback_data)
    # Добавляем кнопку назад
    kb.button(text="Назад", callback_data="back_to_main")
    return kb.as_markup()

def services_list_keyboard(services: list["Service"]) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for service in services:
        label = service.service_name
        callback_data = f"edit_service:{service.service_id}"
        kb.button(text=label, callback_data=callback_data)
    kb.button(text="Назад", callback_data="back_to_main")
    return kb.as_markup()

def masters_list_keyboard(masters: list["Master"]) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for master in masters:
        label = master.master_name
        callback_data = f"edit_master:{master.master_id}"
        kb.button(text=label, callback_data=callback_data)
    kb.button(text="Назад", callback_data="back_to_main")
    return kb.as_markup()
