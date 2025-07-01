from aiogram.types import ReplyKeyboardMarkup, WebAppInfo, InlineKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from sqlalchemy.util import await_only


from app.config import settings



def main_keyboard(user_id: int, first_name: str, has_phone: bool=False) -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    url_applications = f"{settings.BASE_SITE}/applications?user_id={user_id}"
    url_add_application = f'{settings.BASE_SITE}/form?user_id={user_id}&first_name={first_name}'
    print(url_add_application)
    # Проверяем наличие номера телефона


    kb.button(text="🌐 Мои заявки", web_app=WebAppInfo(url=url_applications))
    kb.button(text="📝 Оставить заявку", web_app=WebAppInfo(url=url_add_application))
    if not has_phone:
        kb.button(text="Отправить контакт 📞", request_contact=True)

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


async def admin_keyboard(user_id: int) -> InlineKeyboardMarkup:
    from app.api.users.router import read_users_find_by_id

    url_applications = f"{settings.BASE_SITE}/admin_telegram?admin_id={user_id}"
    url_edit_work_days = f'{settings.BASE_SITE}/work_days?user_id={user_id}'

    kb = InlineKeyboardBuilder()
    kb.button(text="🏠 На главную", callback_data="back_home")
    kb.button(text="📝 Смотреть заявки", web_app=WebAppInfo(url=url_applications))
    # kb.button(text="📝 Смотреть сайт", url="https://7db91ec2-75b8-4079-a086-8d598f685a93.tunnel4.com/")
    kb.button(text="⏰ Редактировать рабочие дни",web_app=WebAppInfo(url=url_edit_work_days))
    user_in_base = await read_users_find_by_id(user_id)
    print(f'упе {user_in_base}')
    if user_in_base is None:
        from app.bot.handlers.registration import create_superuser_button
        kb.row(create_superuser_button)

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
