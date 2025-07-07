import pytest
from httpx import AsyncClient


@pytest.mark.parametrize("name,service,appointment_date,appointment_time,user_id,status_code", [
    ("ilmir112", "1_Сезонная замена",  "2025-07-22", "09:30", 125583082, 200),
])
async def test_add_application(name, service, appointment_date, appointment_time, user_id, status_code, ac: AsyncClient):
    response = await ac.post("/api/appointment", json={
        "name": name,
        "service": service,
        "appointment_date": appointment_date,
        "appointment_time": appointment_time,
        "user_id": user_id,
    })
    assert response.status_code == status_code
