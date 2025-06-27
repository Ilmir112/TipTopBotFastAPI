from datetime import datetime
from typing import List

from pydantic import BaseModel
from sqlalchemy.future import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import joinedload
from sqlalchemy.sql.functions import now

from app.dao.base import BaseDAO
from app.api.users.models import Users, SuperUsers, UserToken
from app.database import async_session_maker


class UsersDAO(BaseDAO):
    model = Users


class SuperUsersDAO(BaseDAO):
    model = SuperUsers

class UserTokenDao(BaseDAO):
    model = UserToken
