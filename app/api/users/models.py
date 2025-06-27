from pydantic import model_validator, field_validator, ConfigDict
from sqlalchemy import String, BigInteger, Integer, Date, Time, ForeignKey, Enum, Interval, Column
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base



class Users(Base):
    __tablename__ = 'users'

    telegram_id: Mapped[int | None] = mapped_column(BigInteger, primary_key=True)
    first_name: Mapped[str] = mapped_column(String, nullable=False)
    username: Mapped[str] = mapped_column(String, nullable=True)
    telephone_number: Mapped[str | None] = mapped_column(String)
    token: Mapped[str | None] = mapped_column(String)

    applications: Mapped[list["Application"]] = relationship(back_populates="user")

    config = ConfigDict(from_attributes=True)

    @model_validator(mode=telephone_number)
    def validate_telephone_number(cls, v):
        # Удаляем все нецифровые символы
        digits = ''.join(filter(str.isdigit, v))
        # Проверка префикса и длины номера
        if v.startswith('7'):
            if len(digits) != 10:
                raise ValueError("Номер должен содержать 11 цифр при префиксе '+7'")
            if not digits.startswith('7'):
                raise ValueError("Некорректный номер: после '+7' должна идти цифра '7'")
        elif v.startswith('8'):
            if len(digits) != 11:
                raise ValueError("Номер должен содержать 11 цифр при начале с '8'")
            if not digits.startswith('8'):
                raise ValueError("Некорректный номер: после '8' должна идти цифра '8'")
        else:
            raise ValueError("Номер должен начинаться с '+7' или '8'")

        return digits

class SuperUsers(Base):
    __tablename__ = "super_users"

    id = Column(Integer, primary_key=True, nullable=False)
    login_user = Column(String, nullable=False)
    name_user = Column(String, nullable=False)
    surname_user = Column(String, nullable=False)
    second_name = Column(String, nullable=False)
    password = Column(String, nullable=False)
    access_level = Column(String, nullable=False)


class UserToken(Base):
    __tablename__ = 'user_tokens'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, unique=True, nullable=False)
    token = Column(String, nullable=False)
