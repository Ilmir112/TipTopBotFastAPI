from pydantic import BaseModel, Field
from datetime import date, time


# Модель для валидации данных
class SWorkingDay(BaseModel):
    working_day:  date = Field(..., description="Дата ")


class WorkingDaysInput(BaseModel):
    date: date

class SUserToken(BaseModel):
    user_id: int
    token: str

