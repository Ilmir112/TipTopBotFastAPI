from typing import Optional

from pydantic import BaseModel, Field
from datetime import date, time


# Модель для валидации данных
class AppointmentData(BaseModel):
    name: str = Field(..., min_length=2, max_length=50, description="Имя клиента")
    service: str = Field(..., min_length=2, max_length=50, description="Услуга клиента")
    # master: str = Field(..., min_length=2, max_length=50, description="Имя мастера")
    appointment_date: date = Field(..., description="Дата назначения")  # Переименовал поле
    appointment_time: time = Field(..., description="Время назначения")  # Переименовал поле
    user_id: Optional[int] = Field(None, description="ID пользователя Telegram")
