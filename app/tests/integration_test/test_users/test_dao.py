
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


@pytest.mark.parametrize(
    "id,first_name,username,auth_date,hash,photo_url,status_code",
    [
        (12345, "TelegramUser", "tele_user_1", 1678886400, "some_hash", "http://example.com/photo.jpg", 200),
        (12346, "TelegramUser2", "tele_user_2", 1678886400, "some_hash", None, 200),
        (12347, "TelegramUser3", "tele_user_3", 1678886400, "invalid_hash", None, 403), # Неверный хеш
    ],
)
async def test_telegram_login(id, first_name, username, auth_date, hash, photo_url, status_code, ac: AsyncClient):
    response = await ac.post(
        "/auth/telegram-login",
        json={
            "id": id,
            "first_name": first_name,
            "username": username,
            "auth_date": auth_date,
            "hash": hash,
            "photo_url": photo_url,
        },
    )
    assert response.status_code == status_code

@pytest.mark.parametrize("expected_status_code", [
    (200),
])
async def test_logout_user(expected_status_code, ac: AsyncClient):
    response = await ac.post("/auth/logout")
    assert response.status_code == expected_status_code

@pytest.mark.parametrize("expected_status_code", [
    (200), # Предполагаем, что пользователь аутентифицирован
    (401), # Если пользователь не аутентифицирован
])
async def test_read_users_me(expected_status_code, authenticated_ac: AsyncClient):
    response = await authenticated_ac.get("/auth/me")
    assert response.status_code == expected_status_code

@pytest.mark.parametrize("expected_status_code", [
    (200),
])
async def test_read_users_all(expected_status_code, ac: AsyncClient):
    response = await ac.get("/auth/all")
    assert response.status_code == expected_status_code
    if expected_status_code == 200:
        assert isinstance(response.json(), list)

@pytest.mark.parametrize("user_id,expected_status_code", [
    (1, 200),
    (999, 200), # Несуществующий ID, вернет null, но статус 200
])
async def test_read_users_find_by_id(user_id, expected_status_code, ac: AsyncClient):
    response = await ac.get(f"/auth/find_by_id?user_id={user_id}")
    assert response.status_code == expected_status_code