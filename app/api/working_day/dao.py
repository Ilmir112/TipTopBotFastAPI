from app.dao.base import BaseDAO
from app.api.working_day.models import WorkingDay


class WorkingDayDAO(BaseDAO):
    model = WorkingDay
