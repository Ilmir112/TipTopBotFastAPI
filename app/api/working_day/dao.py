from datetime import date

from sqlalchemy import select

from app.api.working_day.models import WorkingDay
from app.dao.base import BaseDAO
from app.database import async_session_maker


class WorkingDayDAO(BaseDAO):
    model = WorkingDay

    @classmethod
    async def find_all(cls, **filter_by):
        """
        Асинхронно находит и возвращает все экземпляры модели, удовлетворяющие указанным критериям.
        Если в filter_by есть 'date', то фильтрует по датам больше или равным текущей.

        Аргументы:
            **filter_by: Критерии фильтрации в виде именованных параметров.

        Возвращает:
            Список экземпляров модели.
        """
        async with async_session_maker() as session:
            query = select(cls.model).filter_by(**filter_by)
            if "date" in filter_by:
                query = query.filter(cls.model.date >= date.today())
            result = await session.execute(query)
            return result.scalars().all()
