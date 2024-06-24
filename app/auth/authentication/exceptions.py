from app.auth.exceptions import BaseAuthException


class AuthenticationError(BaseAuthException):
    pass


class AuthenticationRequiredError(AuthenticationError):
    pass


class PasswordError(AuthenticationError):
    pass
