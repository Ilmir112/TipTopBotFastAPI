import pytest
from httpx import AsyncClient


@pytest.mark.parametrize("service_name,time_work,status_code", [
    ("Баланс", "00:08:00",  200),
    ("Балавув", "ddwed", 422),
])
async def test_add_service(service_name, time_work, status_code, authenticated_ac: AsyncClient):
    response = await authenticated_ac.post("/service/add", params={
        "service_name": service_name,
        "time_work": time_work,
    })
    assert response.status_code == status_code
