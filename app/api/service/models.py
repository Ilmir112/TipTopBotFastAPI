from datetime import timedelta

from sqlalchemy import (
    Integer,
    Interval,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Service(Base):
    __tablename__ = "services"

    service_id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )  # Уникальный идентификатор услуги
    service_name: Mapped[str] = mapped_column(String, nullable=False)  # Название услуги
    time_work: Mapped[timedelta] = mapped_column(Interval, nullable=False)

    # Связь с заявками (одна услуга может быть частью нескольких заявок)
    applications: Mapped[list["Application"]] = relationship(
        "Application", back_populates="service", cascade="all, delete"
    )
