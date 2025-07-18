from aiogram.types import KeyboardButton, Message, ReplyKeyboardMarkup

from app.api.users.dao import UsersDAO
from app.bot.keyboards.kbs import main_keyboard


def get_about_us_text() -> str:
    return """1
🔧 ШИНОМОНТАЖ "TIP-TOP" 🔧

Добро пожаловать в мир надежных решений для вашего автомобиля!

✨ Наша миссия:
Обеспечить безопасность и комфорт вашего автомобиля, предлагая 
профессиональный шиномонтаж и обслуживание.

🚗 Наши услуги:
• Замена и балансировка шин
• Ремонт и восстановление шин
• Диагностика и проверка давления
• Хранение сезонных шин
• Установка и снятие колёс

👷‍♂️ Наши мастера:
Опытные специалисты с высокой квалификацией, использующие современное оборудование
 и последние технологии для качественного обслуживания.

🌿 Наша атмосфера:
Комфорт и доверие — наши приоритеты. Мы ценим ваше время и стараемся 
сделать процесс максимально быстрым и удобным.

💎 Почему выбирают нас:
• Индивидуальный подход к каждому клиенту
• Использование сертифицированных материалов и инструментов
• Гарантия на выполненные работы
• Уютная и современная мастерская
• Удобное расположение и гибкий график работы

Обеспечьте безопасность и надежность вашего автомобиля вместе с "TIP-TOP" 🔧
"!
Запишитесь на обслуживание прямо сейчас и доверьте свой автомобиль профессионалам.

✨ Ваша безопасность — наш главный приоритет! ✨
"""


async def greet_user(
    message: Message, is_new_user: bool, has_phone: bool = True
) -> None:
    """
    Приветствует пользователя и отправляет соответствующее сообщение.
    """
    greeting = "Добро пожаловать" if is_new_user else "С возвращением"
    status = "Вы успешно зарегистрированы!" if is_new_user else "Рады видеть вас снова!"
    text = (
        f"{greeting}, <b>{message.from_user.full_name}</b>! {status}\n"
        f"<b>{message.from_user.full_name}</b>!"
        "Чем я могу помочь вам сегодня?"
    )
    await message.answer(text)
    phone_mes = (
        "Для отправки напоминания прошу поделиться номером телефона"
        if has_phone is False
        else text
    )
    if has_phone is False:
        await send_contact_request_keyboard(message)
        return

    await message.answer(
        phone_mes,
        reply_markup=main_keyboard(
            user_id=message.from_user.id,
            first_name=message.from_user.first_name,
            has_phone=has_phone,
        ),
    )


async def user_has_phone(user_id: int) -> bool:
    user = await UsersDAO.find_one_or_none_by_id(data_id=user_id)
    if user:
        if str(user.telephone_number).isdigit():
            return True
    return False


async def send_contact_request_keyboard(message: Message):
    keyboard = ReplyKeyboardMarkup(
        resize_keyboard=True,
        one_time_keyboard=True,
        keyboard=[[KeyboardButton(text="Поделиться номером", request_contact=True)]],
    )
    await message.answer("Пожалуйста, поделитесь своим номером", reply_markup=keyboard)
