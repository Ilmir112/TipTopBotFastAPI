from pydantic import BaseModel, Field, validator, field_validator, ConfigDict
from datetime import date, time, timedelta


class SService(BaseModel):
    service_name: str = Field(..., min_length=2, max_length=70, description="Название услуги")
    time_work: timedelta

    model_config = ConfigDict(arbitrary_types_allowed=True)


    @field_validator('time_work')
    def check_time_work(cls, v):
        total_seconds = v.total_seconds()
        if total_seconds < 10 * 60:
            raise ValueError('Время работы должно быть не менее 10 минут')
        if total_seconds > 1000 * 60:
            raise ValueError('Время работы должно быть не более 1000 минут')
        return v


