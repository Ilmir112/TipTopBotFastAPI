from datetime import timedelta
from tkinter.constants import CASCADE
from wsgiref.validate import validator

from pydantic import model_validator, field_validator, ConfigDict
from sqlalchemy import String, BigInteger, Integer, Date, Time, ForeignKey, Enum, Interval
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.api.users.models import Users
from app.database import Base
import enum



class Application(Base):
    __tablename__ = 'applications'


    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)  # Уникальный идентификатор заявки
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('users.telegram_id'), nullable=True)  # Внешний ключ на пользователя
    # master_id: Mapped[int] = mapped_column(Integer, ForeignKey('masters.master_id'))  # Внешний ключ на мастера
    service_id: Mapped[int] = mapped_column(Integer, ForeignKey('services.service_id'))  # Внешний ключ на услугу
    appointment_date: Mapped[Date] = mapped_column(Date, nullable=False)  # Дата заявки
    appointment_time: Mapped[Time] = mapped_column(Time, nullable=False)  # Время заявки
    # service_type: Mapped[ServiceEnum] = mapped_column(Enum(ServiceEnum), nullable=False)
    client_name: Mapped[str] = mapped_column(String, nullable=False)  # Имя пользователя
    # Связи с пользователем, мастером и услугой
    user: Mapped["Users"] = relationship("Users", back_populates="applications")
    # master: Mapped["Master"] = relationship(back_populates="applications")
    service: Mapped["Service"] = relationship("Service", back_populates="applications")