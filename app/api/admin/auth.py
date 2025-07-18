from sqladmin.authentication import AuthenticationBackend
from starlette.requests import Request

from app.api.users.auth import authenticate_user, create_access_token


class AdminAuth(AuthenticationBackend):
    async def login(self, request: Request) -> bool:
        form = await request.form()
        login_user, password = form["username"], form["password"]
        user = await authenticate_user(login_user, password)
        if user:
            access_token = create_access_token({"sub": str(user.id)})
            request.session.update({"token": access_token})
            return True
        return False

    async def logout(self, request: Request) -> bool:
        # Usually you'd want to just clear the session
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> bool:
        token = request.session.get("token")

        if not token:
            return False
        return True


authentication_backend = AdminAuth(secret_key="...")
