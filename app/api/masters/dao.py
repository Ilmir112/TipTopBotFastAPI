from app.dao.base import BaseDAO
from app.api.masters.models import Master


class MasterDAO(BaseDAO):
    model = Master
