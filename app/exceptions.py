from fastapi import HTTPException, status


class ZimaException(HTTPException):
    status_code = 500
    detail = ""

    def __init__(self):
        super().__init__(status_code=self.status_code, detail=self.detail)


class UserAlreadyExistsException(ZimaException):
    status_code = status.HTTP_409_CONFLICT
    detail = "Пользователь уже существует"


class UnauthorizedException(ZimaException):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Только админ может входить через Telegram."

class IncorectLoginOrPassword(ZimaException):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Неверная логин или пароль"


class TokenExpiredException(ZimaException):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Срок действия токена истек"


class TokenAbsentException(ZimaException):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Токен отсутствует"


class IncorrectTokenFormatException(ZimaException):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Неверный формат токена"