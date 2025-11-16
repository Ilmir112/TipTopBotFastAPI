from audioop import reverse
from datetime import date

from sqlalchemy import select

from app.api.working_day.models import WorkingDay
from app.dao.base import BaseDAO
from app.database import async_session_maker


class WorkingDayDAO(BaseDAO):
    model = WorkingDay

    @classmethod
    async def find_all(cls, start_date: date | None = None, **filter_by):
        """
        Асинхронно находит и возвращает все экземпляры модели, удовлетворяющие указанным критериям.
        Если указан start_date, то фильтрует по датам больше или равным start_date.

        Аргументы:
            start_date: Начальная дата для фильтрации (включительно).
            **filter_by: Критерии фильтрации в виде именованных параметров.

        Возвращает:
            Список экземпляров модели.
        """
        async with async_session_maker() as session:
            query = select(cls.model).filter_by(**filter_by)
            if start_date:
                query = query.filter(cls.model.date >= start_date).order_by(cls.model.date.asc())
            result = await session.execute(query)
            return result.scalars().all()
