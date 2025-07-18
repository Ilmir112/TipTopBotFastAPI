import asyncio
import json
from datetime import datetime, timedelta

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import insert

from app.api.applications.models import Application
from app.api.service.models import Service
from app.api.users.models import SuperUsers, Users
from app.api.working_day.models import WorkingDay
from app.config import settings
from app.database import Base, async_session_maker, engine
from app.main import app as fastapi_app


@pytest.fixture(scope="session", autouse=True)
async def prepare_database():
    assert settings.MODE == "TEST"

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    def open_mock_json(model: str):
        with open(f"app/tests/mock_{model}.json", "r", encoding="utf-8") as file:
            return json.load(file)

    workdays = validate_data_in_timestamp(open_mock_json("workdays"))
    users = validate_data_in_timestamp(open_mock_json("users"))
    service = validate_data_in_timestamp(open_mock_json("service"))
    super_users = validate_data_in_timestamp(open_mock_json("super_users"))
    application = validate_data_in_timestamp(open_mock_json("application"))

    async with async_session_maker() as session:
        for Model, values in [
            (WorkingDay, workdays),
            (Users, users),
            (SuperUsers, super_users),
            (Service, service),
            (Application, application),
        ]:
            query = insert(Model).values(values)
            await session.execute(query)

        await session.commit()


def parse_time_str(time_str):
    hours, minutes, seconds = map(int, time_str.split(":"))
    return timedelta(hours=hours, minutes=minutes, seconds=seconds)


def validate_data_in_timestamp(value_list):
    value_list_new = []
    value_dict_new = {}
    for value_dict in value_list:
        for key, value in value_dict.items():
            if isinstance(value, datetime) or key in ["date", "appointment_date"]:
                value_dict_new[key] = datetime.strptime(value, "%Y-%m-%d")
            # Преобразуем время
            elif key in ["time_work"]:
                value_dict_new[key] = parse_time_str(value)
            elif key in ["appointment_time"]:
                value_dict_new[key] = datetime.strptime(value, "%H:%M")
            else:
                value_dict_new[key] = value
        value_list_new.append(value_dict_new)
    return value_list_new


# Взято из документации к pytest-asyncio
# Создаем новый event loop для прогона тестов
@pytest.fixture(scope="session")
def event_loop(request):
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def ac():
    "Асинхронный клиент для тестирования эндпоинтов"
    async with AsyncClient(
        transport=ASGITransport(app=fastapi_app), base_url="http://test"
    ) as ac:
        yield ac


@pytest.fixture(scope="session")
async def authenticated_ac():
    "Асинхронный аутентифицированный клиент для тестирования эндпоинтов"
    async with AsyncClient(
        transport=ASGITransport(app=fastapi_app), base_url="http://test"
    ) as ac:
        response = await ac.post(
            "/auth/login",
            json={
                "login_user": "ilmir112",
                "password": "1953as",
            },
        )
        if response:
            assert ac.cookies["access_token"]
            yield ac
