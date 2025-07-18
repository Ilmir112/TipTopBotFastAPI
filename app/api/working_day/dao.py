from app.api.working_day.models import WorkingDay
from app.dao.base import BaseDAO


class WorkingDayDAO(BaseDAO):
    model = WorkingDay
