from pydantic import BaseModel, Field


# Модель для валидации данных
class SMaster(BaseModel):
    master_name: str = Field(
        ..., min_length=2, max_length=50, description="Имя мастера"
    )
