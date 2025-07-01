from datetime import datetime, timedelta
from typing import List

from pydantic import BaseModel
from sqlalchemy.future import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import joinedload

from app.dao.base import BaseDAO
from app.api.applications.models import Application
from app.database import async_session_maker

class AppointmentRequest(BaseModel):
    appointment_date: str  # формат 'YYYY-MM-DD'
    appointment_time: str  # формат 'HH:MM'
    # master_id: int



class ApplicationDAO(BaseDAO):
    model = Application

    @classmethod
    async def get_booked_times(cls, appointment_date: str) -> List[str]:

        async with async_session_maker() as session:
            query = select(cls.model.appointment_time).where(cls.model.appointment_date == appointment_date)
            result = await session.execute(query)
            return result.scalars().all()



    # Здесь должна быть логика получения данных из базы
    # Для примера возвращаем статичный список

    @classmethod
    async def is_time_available(cls, appointment_date, appointment_time):
        async with async_session_maker() as session:
            try:
                # Проверяем наличие записи на указанную дату и время для данного мастера
                query = select(cls.model).where(
                    cls.model.appointment_date == appointment_date,
                    cls.model.appointment_time == appointment_time
                )

                result = await session.execute(query)

            except SQLAlchemyError as e:
                print(e)
            existing_record = result.scalar_one_or_none()
            return existing_record is None

    @classmethod
    async def add_appointment_if_available(cls, **values):
        appointment_date = values.get('appointment_date')
        appointment_time = values.get('appointment_time')
        # master_id = values.get('master_id')

        # Проверяем доступность времени
        is_available = await cls.is_time_available(appointment_date, appointment_time)
        if not is_available:
            raise Exception("Выбранное время уже занято.")
            return None



        # Если свободно — добавляем запись
        return await cls.add(**values)

    @classmethod
    async def get_applications_by_user(cls, user_id: int):
        """
        Возвращает все заявки пользователя по user_id с дополнительной информацией
        о мастере и услуге.

        Аргументы:
            user_id: Идентификатор пользователя.

        Возвращает:
            Список заявок пользователя с именами мастеров и услуг.
        """
        async with async_session_maker() as session:
            try:
                # Используем joinedload для ленивой загрузки связанных объектов
                query = (
                    select(cls.model)
                    .options(joinedload(cls.model.service))
                    .where(cls.model.appointment_date <= datetime.now().date() + timedelta(days=7))
                    .filter_by(user_id=user_id)
                )
                result = await session.execute(query)
                if result:
                    applications = result.scalars().all()
                    # Фильтруем заявки по дате и времени
                    future_applications = [
                        app for app in applications
                    ]

                    # Возвращаем список словарей с нужными полями
                    return [
                        {
                            "application_id": app.id,
                            "service_name": app.service.service_name,
                            "appointment_date": app.appointment_date,
                            "appointment_time": app.appointment_time,
                        }
                        for app in future_applications
                    ]
            except SQLAlchemyError as e:
                print(f"Error while fetching applications for user {user_id}: {e}")
                return None

    @classmethod
    async def get_all_applications(cls):
        """
        Возвращает все заявки в базе данных с дополнительной информацией о мастере и услуге.

        Возвращает:
            Список всех заявок с именами мастеров и услуг.
        """
        async with async_session_maker() as session:
            try:
                # Используем joinedload для загрузки связанных данных
                query = (
                    select(cls.model)
                    .options(joinedload(cls.model.service))
                    .where(cls.model.appointment_date >= datetime.now().date() - timedelta(days=5))
                )
                result = await session.execute(query)
                applications = result.scalars().all()

                # Возвращаем список словарей с нужными полями
                return [
                    {
                        "application_id": app.id,
                        "user_id": app.user_id,
                        "service_name": app.service.service_name,  # Название услуги
                        "appointment_date": app.appointment_date,
                        "appointment_time": app.appointment_time,
                        "client_name": app.client_name  # Имя клиента

                    }
                    for app in applications
                ]
            except SQLAlchemyError as e:
                print(f"Error while fetching all applications: {e}")
                return None

