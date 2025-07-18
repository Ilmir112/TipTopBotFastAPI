
import pytest
from httpx import AsyncClient


@pytest.mark.parametrize(
    "first_name,username,telephone_number,status_code",
    [
        ("edede", "ded", "79379977485", 200),
        # ("edede", "ded", "79379977485", 409),
        ("ededwde", "ddwed", "79379973485", 200),
    ],
)
async def test_register(
    first_name, username, telephone_number, status_code, ac: AsyncClient
):
    response = await ac.post(
        "/auth/register",
        json={
            "first_name": first_name,
            "username": username,
            "telephone_number": telephone_number,
        },
    )
    assert response.status_code == status_code


@pytest.mark.parametrize(
    "login_user,name_user,surname_user,second_name,"
    "password,access_level,telegram_id,status_code",
    [
        ("Ilmir1", "vfv", "edede", "ded", "195312", "admin", 1, 200),
        ("edede", "ded", "edede", "ded", "eded", "ded", 1, 422),
    ],
)
async def test_super_user_register(
    login_user,
    name_user,
    surname_user,
    second_name,
    password,
    access_level,
    telegram_id,
    status_code,
    ac: AsyncClient,
):
    response = await ac.post(
        "/auth/register_super_user",
        json={
            "login_user": login_user,
            "name_user": name_user,
            "surname_user": surname_user,
            "second_name": second_name,
            "password": password,
            "access_level": access_level,
            "telegram_id": telegram_id,
        },
    )
    assert response.status_code == status_code


@pytest.mark.parametrize(
    "login_user,password,status_code",
    [
        ("Ilmir1", "195312", 200),
        ("ilmir112", "1234563", 401),
        ("ilmir12", "123456", 401),
    ],
)
async def test_login(login_user, password, status_code, ac: AsyncClient):
    response = await ac.post(
        "/auth/login",
        json={
            "login_user": login_user,
            "password": password,
        },
    )
    # print(response)
    assert response.status_code == status_code
