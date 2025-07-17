import asyncio
import logging
from contextlib import asynccontextmanager

import aiogram
import uvicorn
from fastapi.exceptions import RequestValidationError
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse

from app.api.admin.auth import authentication_backend
from app.api.admin.views import ApplicationAdmin
# from app.api.admin.views import MastersAdmin
from app.api.admin.views import ServiceAdmin
from app.api.admin.views import UserAdmin
from app.bot.create_bot import bot, dp, stop_bot, start_bot
from app.bot.handlers.admin_router import admin_router
from app.bot.handlers.send_message import send_reminders
from app.bot.handlers.user_router import user_router
from app.config import settings
from app.database import engine
from app.logger import logger
from app.pages.router import router as router_pages
from app.api.applications.router import router as router_applications
from app.api.users.router import router as router_users
# from app.api.masters.router import router as router_masters
from app.api.service.router import router as router_service
from app.api.working_day.router import router as router_working_day
from fastapi.staticfiles import StaticFiles
from aiogram.types import Update
from fastapi import FastAPI, Request
from sqladmin import Admin

from apscheduler.schedulers.asyncio import AsyncIOScheduler



scheduler = AsyncIOScheduler()


async def start_scheduler():
    if not scheduler.running:
        scheduler.add_job(send_reminders, 'interval', hours=1)
        scheduler.start()


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


@asynccontextmanager
async def lifespan(app: FastAPI):
    logging.info("Starting bot setup...")
    dp.include_router(user_router)
    dp.include_router(admin_router)
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

app = FastAPI(lifespan=lifespan)

# app.mount('/static', StaticFiles(directory='app/static'), 'static')
app.mount('/static', StaticFiles(directory='static'), 'static')


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
        loc = err.get('loc', [])
        msg = err.get('msg', '')
        # Обычно loc содержит ['body', 'parameter_name']
        if len(loc) > 1:
            param_name = loc[-1]
        else:
            param_name = loc[0] if loc else 'unknown'
        invalid_params.append({param_name: msg})

    logging.error(f"validation_exception: {errors}, body: {invalid_params}")
    return JSONResponse(
        status_code=422,
        content={
            "detail": errors,
            "invalid_params": invalid_params,
            "body": exc.body,
            "message": "validation exception"
        },
    )


app.include_router(router_pages)
# app.include_router(router_masters)
app.include_router(router_service)
app.include_router(router_working_day)
app.include_router(router_applications)
app.include_router(router_users)

origins = [
    "http://localhost:3000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS", "DELETE", "PATCH", "PUT"],
    allow_headers=[
        "Content-Type",
        "Set-Cookie",
        "Access-Control-Allow-Headers",
        "Access-Control-Allow-Origin",
        "Authorization",
    ],
)

# @app.middleware("http")
# async def log_requests(request: Request, call_next):
#     body = await request.body()
#     logging.info(f"Received request: {request.method} {request.url} headers: {request.headers} body: {body}")
#     response = await call_next(request)
#     return response

admin = Admin(app, engine, authentication_backend=authentication_backend)

admin.add_view(UserAdmin)
# admin.add_view(MastersAdmin)
admin.add_view(ServiceAdmin)
admin.add_view(ApplicationAdmin)

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
