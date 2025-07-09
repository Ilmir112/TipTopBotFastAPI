import os
from typing import Literal
from urllib.parse import quote
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from faststream.rabbit import RabbitBroker
from pydantic import ValidationError, ConfigDict
from pydantic_settings import BaseSettings

# from app.logger import logger


class Settings(BaseSettings):
    MODE: Literal["DEV", "TEST", "PROD"]
    LOG_LEVEL: Literal["DEV", "TEST", "PROD", "INFO"]
    DB_USER: str
    DB_PASSWORD: str
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str
    # DATABASE_URL: str = None

    BOT_TOKEN: str
    BASE_SITE: str
    ADMIN_LIST: list
    ADMIN_ID: str

    def get_webhook_url(self) -> str:
        """Возвращает URL вебхука с кодированием специальных символов."""
        return f"{self.BASE_SITE}/webhook"

    # @property
    # def rabbitmq_url(self) -> str:
    #     return (
    #         f"amqp://{self.RABBITMQ_USERNAME}:{quote(self.RABBITMQ_PASSWORD)}@"
    #         f"{self.RABBITMQ_HOST}:{self.RABBITMQ_PORT}/{self.VHOST}"
    #     )


    @property
    def DATABASE_URL(self):
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    TEST_DB_USER: str
    TEST_DB_PASSWORD: str
    TEST_DB_HOST: str
    TEST_DB_PORT: int
    TEST_DB_NAME: str

    @property
    def TEST_DATABASE_URL(self):
        return (
            f"postgresql+asyncpg://{self.TEST_DB_USER}:{self.TEST_DB_PASSWORD}@"
            f"{self.TEST_DB_HOST}:{self.TEST_DB_PORT}/{self.TEST_DB_NAME}"
        )

    SMTP_HOST: str
    SMTP_PORT: int
    SMTP_USER: str
    SMTP_PASS: str

    REDIS_HOST: str
    REDIS_PORT: int

    HAWK_DSN: str

    SECRET_KEY: str
    ALGORITHM: str

    TOKEN: str
    CHAT_ID: str

    model_config = ConfigDict(env_file = ".env")
    # model_config = ConfigDict(env_file = '../.env')



try:
    # Создайте экземпляр класса Settings
    settings = Settings()
    log_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "log.txt")
    # logger.add(log_file_path, format=settings.FORMAT_LOG, level="INFO", rotation=settings.LOG_ROTATION)
    # broker = RabbitBroker(url=settings.rabbitmq_url)
    # scheduler = AsyncIOScheduler(jobstores={'default': SQLAlchemyJobStore(url=settings.STORE_URL)})

    # Для проверки
except ValidationError as e:
    print(f"Ошибка валидации: {e}")
    print(e)
