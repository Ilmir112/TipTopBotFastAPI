from pydantic import BaseModel, ConfigDict, Field


# Модель для валидации данных
class SUsers(BaseModel):
    first_name: str = Field(..., min_length=2, max_length=50, description="Полное имя")
    username: str = Field(
        ..., min_length=2, max_length=50, description="Сокращенное имя"
    )
    telephone_number: str = Field(
        ..., min_length=2, max_length=50, description="номер телефона"
    )  # Переименовал поле

    model_config = ConfigDict(arbitrary_types_allowed=True)


class STelegramUser(BaseModel):
    id: int
    first_name: str | None = None
    last_name: str | None = None
    username: str | None = None
    photo_url: str | None = None
    auth_date: int
    hash: str


class SUsersRegister(BaseModel):
    login_user: str = Field(..., min_length=2, max_length=50, description="Логин")
    name_user: str = Field(..., min_length=2, max_length=50, description="имя")
    surname_user: str = Field(..., min_length=2, max_length=50, description="Отчество")
    second_name: str = Field(..., min_length=2, max_length=50, description="Фамилия")
    password: str = Field(..., min_length=5, max_length=50, description="пароль")
    access_level: str = Field(
        ..., min_length=2, max_length=50, description="Уровень доступа"
    )
    telegram_id: int = Field(..., description="ID telegram")

    model_config = ConfigDict(arbitrary_types_allowed=True)


class SUsersAuth(BaseModel):
    login_user: str
    password: str
