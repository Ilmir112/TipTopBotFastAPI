from typing import Literal

from pydantic import ValidationError, ConfigDict
from pydantic_settings import BaseSettings


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
    ADMIN_ID: int

    def get_webhook_url(self) -> str:
        """Возвращает URL вебхука с кодированием специальных символов."""
        return f"{self.BASE_SITE}/webhook"

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

    def get_webhook_url(self) -> str:
        """Возвращает URL вебхука с кодированием специальных символов."""
        return f"{self.BASE_SITE}/webhook"

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

    # model_config = ConfigDict(env_file = ".env")
    model_config = ConfigDict(env_file = '../.env')



try:
    # Создайте экземпляр класса Settings
    settings = Settings()

    # Для проверки
except ValidationError as e:
    print(f"Ошибка валидации: {e}")
    print(e)
