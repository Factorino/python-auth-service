from auth_service.domain.value_objects import Username


class AuthenticationError(Exception):
    pass


class UserAlreadyExistsError(AuthenticationError):
    def __init__(self, username: Username) -> None:
        super().__init__(f"User '{username}' already exists.")


class UserNotFoundError(AuthenticationError):
    def __init__(self, username: Username) -> None:
        super().__init__(f"User '{username}' was not found.")


class InvalidCredentialsError(AuthenticationError):
    def __init__(self) -> None:
        super().__init__("Invalid credentials.")
