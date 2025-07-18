from app.api.users.models import SuperUsers, Users
from app.dao.base import BaseDAO


class UsersDAO(BaseDAO):
    model = Users


class SuperUsersDAO(BaseDAO):
    model = SuperUsers
