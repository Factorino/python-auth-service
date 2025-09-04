import re
from dataclasses import dataclass
from typing import ClassVar


@dataclass(frozen=True, slots=True)
class Username:
    value: str

    # Allowed characters: letters, numbers, underscore, minus
    # From 3 to 30 characters
    _pattern: ClassVar[re.Pattern] = re.compile(r"^[a-zA-Z0-9_-]{3,30}$")

    def __post_init__(self) -> None:
        if not self.value or not isinstance(self.value, str):
            raise ValueError("Username cannot be empty")
        if len(self.value) < 3:
            raise ValueError("Username must be at least 3 characters long")
        if len(self.value) > 30:
            raise ValueError("Username must be no more than 30 characters long")
        if not self._pattern.match(self.value):
            raise ValueError(
                "Username can only contain letters, numbers, _ and - symbols"
            )

    def __str__(self) -> str:
        return self.value

    def __eq__(self, other) -> bool:
        if not isinstance(other, Username):
            return False
        return self.value == other.value

    def __hash__(self) -> int:
        return hash(self.value)
