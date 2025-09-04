class UserAlreadyExistsError(Exception):
    def __init__(self, username: str) -> None:
        super().__init__(f"User with username '{username}' already exists")


class UserNotFoundError(Exception):
    def __init__(self, user_id: str) -> None:
        super().__init__(f"User with ID '{user_id}' not found")


class InvalidCredentialsError(Exception):
    def __init__(self) -> None:
        super().__init__("Invalid username or password")
