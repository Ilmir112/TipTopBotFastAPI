from sqlalchemy import String, Integer, Date
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class WorkingDay(Base):
    __tablename__ = 'working_day'

    id: Mapped[int] = mapped_column(Integer, primary_key=True,
                                           autoincrement=True)  # Уникальный идентификатор
    date: Mapped[Date] = mapped_column(Date, unique=True, nullable=False)  # Имя мастера

    # # Связь с заявками (один мастер может иметь несколько заявок)
    # applications: Mapped[list["Application"]] = relationship(back_populates="master")
