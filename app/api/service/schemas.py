import re
from datetime import date, time, timedelta

from pydantic import BaseModel, ConfigDict, Field, field_validator, validator


class SService(BaseModel):
    service_name: str = Field(
        ..., min_length=2, max_length=70, description="Название услуги"
    )
    time_work: timedelta

    model_config = ConfigDict(arbitrary_types_allowed=True)

    @field_validator("time_work")
    def parse_time_work(cls, v):
        if isinstance(v, str):
            # Парсим строку формата HH:MM:SS
            match = re.match(r"^(\d+):(\d+):(\d+)$", v)
            if not match:
                raise ValueError("Некорректный формат времени. Ожидается HH:MM:SS")
            hours, minutes, seconds = map(int, match.groups())
            print(hours, minutes, seconds)
            return timedelta(hours=hours, minutes=minutes, seconds=seconds)
        return v

    # @field_validator('check_time_work')
    # def check_time_work(cls, v):
    #     total_seconds = v.total_seconds()
    #     if total_seconds < 10 * 60:
    #         raise ValueError('Время работы должно быть не менее 10 минут')
    #     if total_seconds > 1000 * 60:
    #         raise ValueError('Время работы должно быть не более 1000 минут')
    #     return v
