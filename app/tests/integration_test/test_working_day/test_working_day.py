import pytest
from httpx import AsyncClient


@pytest.mark.parametrize("working_day,status_code", [("2025-08-01", 200)])
async def test_add_working_day(working_day, status_code, ac: AsyncClient):
    response = await ac.post(
        "/day/add",
        json={
            "working_day": working_day,
        },
    )
    assert response.status_code == status_code
