from app.api.masters.models import Master
from app.dao.base import BaseDAO


class MasterDAO(BaseDAO):
    model = Master
