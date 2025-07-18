import pytest
from httpx import AsyncClient


@pytest.mark.parametrize(
    "name,service,appointment_date,appointment_time,user_id,working_day_id,status_code",
    [
        ("ilmir112", "1_Сезонная замена", "2025-07-27", "09:30", 1, 1, 200),
        ("ilmir112", "1_Сезонная замена", "2025-07-30", "09:30", 1, 4, 409),
        ("ilmir112", "1_Сезонная замена", "2025-13-30", "09:30", 1, 4, 422),
    ],
)
async def test_add_application(
    name,
    service,
    appointment_date,
    appointment_time,
    user_id,
    working_day_id,
    status_code,
    ac: AsyncClient,
):
    response = await ac.post(
        "/api/appointment",
        json={
            "name": name,
            "service": service,
            "appointment_date": appointment_date,
            "appointment_time": appointment_time,
            "user_id": user_id,
            "working_day_id": working_day_id,
        },
    )
    assert response.status_code == status_code


@pytest.mark.parametrize("application_id,status_code", [(2, 200), (30, 404)])
async def test_delete(application_id, status_code, ac: AsyncClient):
    response = await ac.delete("/api/delete", params={"application_id": application_id})
    assert response.status_code == status_code
