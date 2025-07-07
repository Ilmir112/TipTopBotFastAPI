from pydantic import BaseModel, Field, ConfigDict
from datetime import date


# Модель для валидации данных
class SWorkingDay(BaseModel):
    working_day:  date = Field(..., description="Дата")
    model_config = ConfigDict(arbitrary_types_allowed=True)


class WorkingDaysInput(BaseModel):
    date: date


class SUserToken(BaseModel):
    user_id: int
    token: str

