from sqladmin import ModelView

from app.api.applications.models import Application
# from app.api.masters.models import Master
from app.api.service.models import Service
from app.api.users.models import Users


class UserAdmin(ModelView, model=Users):
    column_list = [c.name for c in Users.__table__.c][:-2]

    name = 'Пользователь'
    name_plural = 'Пользователи'

#
# class MastersAdmin(ModelView, model=Master):
#     column_list = [c.name for c in Master.__table__.c][:-2]
#
#     name = 'Мастер'
#     name_plural = 'Мастера'

class ServiceAdmin(ModelView, model=Service):
    column_list = [c.name for c in Service.__table__.c][:-2]

    name = 'Услуга'
    name_plural = 'Услуги'

class ApplicationAdmin(ModelView, model=Application):
    column_list = ([c.name for c in Application.__table__.c][4:-2] +
                   ['service.service_name'] +
                   ['user.telephone_number'])

    name = 'Запись'
    name_plural = 'Записи'


