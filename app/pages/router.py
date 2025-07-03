

from fastapi import APIRouter

from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
from fastapi.responses import HTMLResponse


from app.api.service.dao import ServiceDAO
from app.api.applications.dao import ApplicationDAO
from app.api.users.dao import UsersDAO
from app.api.users.dependencies import get_current_user
from app.api.users.models import Users
from app.api.working_day.dao import WorkingDayDAO
from app.api.working_day.router import find_working_day_all
from app.config import settings

router = APIRouter(prefix='', tags=['Фронтенд'])
templates = Jinja2Templates(directory='app/templates')
# templates = Jinja2Templates(directory='templates')


@router.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html",
                                      {"request": request, "title": ""})


@router.get("/work_days", response_class=HTMLResponse)
async def read_work_days_root(request: Request, user_id: int):
    if user_id == settings.ADMIN_ID:

        work_days = await WorkingDayDAO.find_all()
        working_days = list(map(lambda x: x.date.strftime("%Y-%m-%d"), work_days))
        data_page = {"request": request,
                     "user_id": user_id,
                     "work_days": working_days,
                     "title": "Изменение рабочих дней"}

        return templates.TemplateResponse("calendar.html", data_page)



@router.get("/form", response_class=HTMLResponse)
async def read_root(request: Request, user_id: int = None, first_name: str = None):
    services = await ServiceDAO.find_all()
    working_days = await WorkingDayDAO.find_all()
    working_days = list(map(lambda x: x.date.strftime("%Y-%m-%d"), working_days))

    data_page = {"request": request,
                 "user_id": user_id,
                 "first_name": first_name,
                 "title": "Запись на шиномонтаж",
                 # "masters": masters,
                 "services": services,
                 "working_days": working_days}

    return templates.TemplateResponse("form.html", data_page)


@router.get("/find_all_service")
async def find_all_service():
    services = await ServiceDAO.find_all()

    return services


@router.get("/admin_telegram", response_class=HTMLResponse)
async def read_root(request: Request, admin_id: int = None):
    data_page = {"request": request, "access": False, 'title_h1': "Панель администратора"}
    if admin_id is None or admin_id != settings.ADMIN_ID:
        data_page['message'] = 'У вас нет прав для получения информации о заявках!'
        return templates.TemplateResponse("applications.html", data_page)
    else:
        data_page['access'] = True
        data_page['applications'] = await ApplicationDAO.get_all_applications()
        return templates.TemplateResponse("applications_admin.html", data_page)


@router.get("/applications", response_class=HTMLResponse)
async def read_root(request: Request, user_id: int = None):
    data_page = {"request": request, "access": False, 'title_h1': "Мои записи"}
    user_check = await UsersDAO.find_one_or_none(telegram_id=user_id)

    if user_id is None or user_check is None:
        data_page['message'] = 'Пользователь по которому нужно отобразить заявки не указан или не найден в базе данных'
        return templates.TemplateResponse("applications.html", data_page)
    else:
        applications = await ApplicationDAO.get_applications_by_user(user_id=user_id)
        data_page['access'] = True
        if len(applications):
            data_page['applications'] = await ApplicationDAO.get_applications_by_user(user_id=user_id)

            return templates.TemplateResponse("applications.html", data_page)
        else:
            data_page['message'] = 'У вас нет заявок!'
            return templates.TemplateResponse("applications.html", data_page)
