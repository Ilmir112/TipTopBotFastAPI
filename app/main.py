import asyncio
import logging
from contextlib import asynccontextmanager
from datetime import date, timedelta
from typing import Optional, List

import aiogram
import uvicorn
from aiogram.types import Update
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import FastAPI, Request, status, Depends, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.staticfiles import StaticFiles
from sqladmin import Admin
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse, RedirectResponse
from faststream.rabbit import RabbitBroker
from starlette.middleware.base import BaseHTTPMiddleware

from app.api.admin.auth import authentication_backend
from app.api.users.models import Users
# from app.api.admin.views import MastersAdmin
from app.api.admin.views import ApplicationAdmin, ServiceAdmin, UserAdmin
from app.api.applications.router import router as router_applications
from app.api.working_day.dao import WorkingDayDAO

# from app.api.masters.router import router as router_masters
from app.api.service.router import router as router_service
from app.api.users.router import router as router_users
from app.api.working_day.router import router as router_working_day
from app.bot.create_bot import bot, dp, start_bot, stop_bot
from app.bot.handlers.admin_router import admin_router
from app.bot.handlers.send_message import send_reminders
from app.bot.handlers.user_router import user_router
from app.config import settings, router_broker
from app.database import engine
from app.logger import logger
from app.pages.router import router as router_pages
from app.rabbit.consumer import start_consumer
from app.api.users.dependencies import get_current_user, get_optional_current_user
from app.exceptions import TokenAbsentException, UnauthorizedException

scheduler = AsyncIOScheduler()


async def check_and_notify_working_days():
    today = date.today()
    # Определяем следующее воскресенье
    days_until_sunday = (6 - today.weekday() + 7) % 7 # 0=понедельник, 6=воскресенье
    next_sunday = today + timedelta(days=days_until_sunday)

    # Проверяем рабочие дни на следующую неделю (например, с понедельника по воскресенье следующей недели)
    next_week_start = next_sunday + timedelta(days=1) # Понедельник следующей недели
    next_week_end = next_week_start + timedelta(days=6) # Воскресенье следующей недели

    missing_days = []
    for i in range(7):
        current_day = next_week_start + timedelta(days=i)
        existing_day = await WorkingDayDAO.find_one_or_none(date=current_day)
        if not existing_day:
            missing_days.append(current_day.strftime("%Y-%m-%d"))

    if missing_days:
        message = "Напоминание: следующие рабочие дни на следующую неделю не установлены:\n"
        message += "\n".join(missing_days)
        message += "\nПожалуйста, добавьте их."
        
        if settings.MODE != "TEST":
            for admin_id in settings.ADMIN_LIST:
                try:
                    await bot.send_message(chat_id=admin_id, text=message)
                except Exception as e_bot:
                    logging.error(f"Ошибка при отправке сообщения бота администратору {admin_id}: {e_bot}", exc_info=True)
    else:
        logging.info("Все рабочие дни на следующую неделю установлены.")


async def start_scheduler():
    if not scheduler.running:
        scheduler.add_job(send_reminders, "interval", hours=1)
        scheduler.add_job(check_and_notify_working_days, "cron", day_of_week='sun', hour=15) # 20:00 каждое воскресенье
        scheduler.add_job(check_and_notify_working_days, "cron", day_of_week='sun', hour=16) # 21:00 каждое воскресенье
        scheduler.start()


logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logging.info("Starting bot setup...")
    dp.include_router(user_router)
    dp.include_router(admin_router)
    # consumer_task = asyncio.create_task(start_consumer())
    logging.info("broker start.")
    await start_bot()
    webhook_url = settings.get_webhook_url()

    # Запуск планировщика задач
    await start_scheduler()

    await setup_webhook(webhook_url)

    logging.info(f"Webhook set to {webhook_url}")
    yield
    logging.info("Shutting down bot...")
    await bot.delete_webhook()
    await stop_bot()
    logging.info("Webhook deleted")
    # if consumer_task:
    #     consumer_task.cancel()
    #     try:
    #         await consumer_task
    #     except asyncio.CancelledError:
    #         print("Потребитель остановлен")
    print("Завершение работы приложения")


async def setup_webhook(webhook_url):
    try:
        # Проверяем текущий статус webhook
        info = await bot.get_webhook_info()
        if info.url != webhook_url:
            await bot.set_webhook(url=webhook_url)

        else:
            print("Webhook уже установлен.")
    except aiogram.exceptions.TelegramRetryAfter as e:
        wait_time = int(e.retry_after)
        print(f"Превышен лимит запросов. Повтор через {wait_time} секунд.")
        await asyncio.sleep(wait_time)
        await setup_webhook(webhook_url)
    except Exception as e:
        print(f"Ошибка при установке webhook: {e}")


class CSPMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["Content-Security-Policy"] = "frame-ancestors 'self' https://zima-krs.ru https://www.zima-krs.ru https://oauth.telegram.org; script-src 'self' https://telegram.org 'unsafe-inline' 'unsafe-eval';"
        return response


app = FastAPI(lifespan=lifespan)
try:
    app.mount("/static", StaticFiles(directory="app/static"), "static")
except Exception as e:
    app.mount('/static', StaticFiles(directory='static'), 'static')

# app.add_middleware(CSPMiddleware)


@app.post("/webhook")
async def webhook(request: Request) -> None:
    # body = await request.body()
    # logger.info(f"Received webhook request: {body}")
    update = Update.model_validate(await request.json(), context={"bot": bot})

    await dp.feed_update(bot, update)
    logger.info("Update processed")


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = exc.errors()
    invalid_params = []

    for err in errors:
        loc = err.get("loc", [])
        msg = err.get("msg", "")
        # Обычно loc содержит ['body', 'parameter_name']
        if len(loc) > 1:
            param_name = loc[-1]
        else:
            param_name = loc[0] if loc else "unknown"
        invalid_params.append({param_name: msg})

    logging.error(f"validation_exception: {errors}, body: {invalid_params}")
    return JSONResponse(
        status_code=422,
        content={
            "detail": errors,
            "invalid_params": invalid_params,
            "body": exc.body,
            "message": "validation exception",
        },
    )


@app.get("/", response_class=RedirectResponse, status_code=status.HTTP_302_FOUND)
async def root(request: Request, current_user: Optional[Users] = Depends(get_optional_current_user)):
    if current_user:
        return RedirectResponse(url="/form", status_code=status.HTTP_302_FOUND)
    else:
        return RedirectResponse(url="/telegram_login", status_code=status.HTTP_302_FOUND)

app.include_router(router_pages)
# app.include_router(router_masters)
app.include_router(router_service)
app.include_router(router_working_day)
app.include_router(router_applications)
app.include_router(router_users)

origins = ["http://localhost:3000"]

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=origins,
#     allow_credentials=True,
#     allow_methods=["GET", "POST", "OPTIONS", "DELETE", "PATCH", "PUT"],
#     allow_headers=[
#         "Content-Type",
#         "Set-Cookie",
#         "Access-Control-Allow-Headers",
#         "Access-Control-Allow-Origin",
#         "Authorization",
#     ],
# )


@app.middleware("http")
async def log_requests(request: Request, call_next):
    body = await request.body()
    logging.info(f"Received request: {request.method} {request.url} headers: {request.headers} body: {body}")
    response = await call_next(request)
    return response


admin = Admin(app, engine, authentication_backend=authentication_backend, base_url="/tiptop")

admin.add_view(UserAdmin)
# admin.add_view(MastersAdmin)
admin.add_view(ServiceAdmin)
admin.add_view(ApplicationAdmin)

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
