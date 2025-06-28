import asyncio
import json
from datetime import datetime

import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy import insert

from app.config import settings
from app.database import Base, async_session_maker, engine
from app.api.users.models import Users, SuperUsers
from app.api.service.models import Service
from app.api.working_day.models import WorkingDay
from app.api.applications.models import Application
from app.main import app


@pytest.fixture(scope="session", autouse=True)
async def prepare_database():
    assert settings.MODE == "TEST"

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    def open_mock_json(model: str):
        with open(f"app/tests/mock_{model}.json", "r") as file:
            return json.load(file)

    users = validate_data_in_timestamp(open_mock_json("users"))
    service = validate_data_in_timestamp(open_mock_json("service"))
    super_users = validate_data_in_timestamp(open_mock_json("super_users"))
    # application = validate_data_in_timestamp(open_mock_json("application"))
    # workdays = validate_data_in_timestamp(open_mock_json("workdays"))

    async with async_session_maker() as session:
        for Model, values in [
            (Users, users),
            (SuperUsers, super_users),
            (Service, service),
            # (Application, application),
            # (WorkingDay, workdays),
        ]:
            query = insert(Model).values(values)
            await session.execute(query)

        await session.commit()


def validate_data_in_timestamp(value_list):
    value_list_new = []
    value_dict_new = {}
    for value_dict in value_list:
        for key, value in value_dict.items():
            if isinstance(value, datetime):
                value_dict_new[key] = datetime.strptime(value, "%Y-%m-%d")
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
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac


@pytest.fixture(scope="session")
async def authenticated_ac():
    "Асинхронный аутентифицированный клиент для тестирования эндпоинтов"
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        await ac.post(
            "/auth/login",
            json={
                "email": "test@test.com",
                "password": "test",
            },
        )
        assert ac.cookies["access_token"]
        yield ac