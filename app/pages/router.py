import hmac
from datetime import date
from typing import Annotated

from fastapi import APIRouter, Query
from fastapi.requests import Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from jose import jwt
from starlette.responses import PlainTextResponse, RedirectResponse

from app.api.applications.dao import ApplicationDAO
from app.api.service.dao import ServiceDAO
from app.api.users.dao import UsersDAO
from app.api.working_day.dao import WorkingDayDAO
from app.config import settings
from app.logger import logger

router = APIRouter(prefix="", tags=["Фронтенд"])
templates = Jinja2Templates(directory="app/templates")


# templates = Jinja2Templates(directory='templates')


@router.get('/telegram-callback')
async def telegram_callback(
        request: Request,
        user_id: Annotated[int, Query(alias='id')],
        query_hash: Annotated[str, Query(alias='hash')],
        next_url: Annotated[str, Query(alias='next')] = '/',
):
    params = request.query_params.items()
    data_check_string = '\n'.join(sorted(f'{x}={y}' for x, y in params if x not in ('hash', 'next')))
    computed_hash = hmac.new(settings.BOT_TOKEN.digest(), data_check_string.encode(), 'sha256').hexdigest()
    is_correct = hmac.compare_digest(computed_hash, query_hash)
    if not is_correct:
        return PlainTextResponse('Authorization failed. Please try again', status_code=401)

    token = jwt.encode({'alg': 'HS256'}, {'k': user_id}, JWT_SECRET_KEY)
    response = RedirectResponse(next_url)
    response.set_cookie(key=COOKIE_NAME, value=token)
    return response


@router.get('/logout')
async def logout():
    response = RedirectResponse('/')
    response.delete_cookie(key=COOKIE_NAME)
    return response


@router.get('<path:path>')
async def unknown(path: str):
    return PlainTextResponse('Not found', status_code=404)


@router.get("/index", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "title": ""})


@router.get("/work_days", response_class=HTMLResponse)
async def read_work_days_root(request: Request, user_id: int):
    try:
        if user_id in settings.ADMIN_LIST:
            work_days = await WorkingDayDAO.find_all()
            working_days = list(map(lambda x: x.date.strftime("%Y-%m-%d"), work_days))
            data_page = {
                "request": request,
                "user_id": user_id,
                "work_days": working_days,
                "title": "Изменение рабочих дней",
            }

            return templates.TemplateResponse("calendar.html", data_page)
    except Exception as e:
        logger.error(e)


@router.get("/form", response_class=HTMLResponse)
async def read_root(request: Request, user_id: int = None, first_name: str = None):
    try:
        services = await ServiceDAO.find_all()
        working_days = await WorkingDayDAO.find_all()
        working_days = list(map(lambda x: x.date.strftime("%Y-%m-%d"), working_days))

        data_page = {
            "request": request,
            "user_id": user_id,
            "first_name": first_name,
            "title": "Запись на шиномонтаж",
            # "masters": masters,
            "services": services,
            "working_days": working_days,
        }

        return templates.TemplateResponse("form.html", data_page)
    except Exception as e:
        logger.error(e)


@router.get("/find_all_service")
async def find_all_service():
    try:
        services = await ServiceDAO.find_all()

        return services
    except Exception as e:
        logger.error(e)


@router.get("/admin_telegram", response_class=HTMLResponse)
async def read_root(request: Request, admin_id: int = None):
    try:
        selected_date_str = request.query_params.get("date")
        if selected_date_str:
            selected_date = date.fromisoformat(selected_date_str)
        else:
            selected_date = date.today()
            selected_date_str = selected_date.isoformat()
        data_page = {
            "request": request,
            "access": False,
            "title_h1": "Панель администратора",
            "selected_date": selected_date_str,
        }
        if admin_id is None or admin_id not in settings.ADMIN_LIST:
            data_page["message"] = "У вас нет прав для получения информации о заявках!"
            return templates.TemplateResponse("applications.html", data_page)
        else:
            data_page["access"] = True
            data_page["applications"] = await ApplicationDAO.get_all_applications(
                selected_date
            )
            return templates.TemplateResponse("applications_admin.html", data_page)
    except Exception as e:
        logger.error(e)


@router.get("/applications", response_class=HTMLResponse)
async def read_root(request: Request, user_id: int = None):
    try:
        data_page = {"request": request, "access": False, "title_h1": "Мои записи"}
        user_check = await UsersDAO.find_one_or_none(telegram_id=user_id)

        if user_id is None or user_check is None:
            data_page["message"] = (
                "Пользователь по которому нужно отобразить заявки не указан или не найден в базе данных"
            )
            return templates.TemplateResponse("applications.html", data_page)
        else:
            applications = await ApplicationDAO.get_applications_by_user(
                user_id=user_id
            )
            data_page["access"] = True
            if len(applications):
                data_page["applications"] = (
                    await ApplicationDAO.get_applications_by_user(user_id=user_id)
                )

                return templates.TemplateResponse("applications.html", data_page)
            else:
                data_page["message"] = "У вас нет заявок!"
                return templates.TemplateResponse("applications.html", data_page)
    except Exception as e:
        logger.error(e)
