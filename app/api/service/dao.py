from app.api.service.models import Service
from app.dao.base import BaseDAO


class ServiceDAO(BaseDAO):
    model = Service
