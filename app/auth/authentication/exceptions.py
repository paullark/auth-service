from app.auth.exceptions import BaseAuthException


class AuthenticationError(BaseAuthException):
    pass


class TokenDataError(AuthenticationError):
    pass


class PasswordError(AuthenticationError):
    pass


class NotEnoughPermissionError(AuthenticationError):
    pass
