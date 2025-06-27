

from app.dao.base import BaseDAO
from app.api.service.models import Service
from app.database import async_session_maker


class ServiceDAO(BaseDAO):
    model = Service



