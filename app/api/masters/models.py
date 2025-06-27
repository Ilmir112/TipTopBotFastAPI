from sqlalchemy import String, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class Master(Base):
    __tablename__ = 'masters'

    master_id: Mapped[int] = mapped_column(Integer, primary_key=True,
                                           autoincrement=True)  # Уникальный идентификатор мастера
    master_name: Mapped[str] = mapped_column(String, nullable=False)  # Имя мастера

    # # Связь с заявками (один мастер может иметь несколько заявок)
    # applications: Mapped[list["Application"]] = relationship(back_populates="master")

