import re
from dataclasses import dataclass
from typing import ClassVar


@dataclass(frozen=True, slots=True)
class Password:
    value: str

    # At least 8 characters, at least one digit, one letter, one special
    _min_length: ClassVar[int] = 8

    def __post_init__(self) -> None:
        if len(self.value) < self._min_length:
            raise ValueError(
                f"Password must be at least {self._min_length} characters long"
            )
        if not re.search(r"[a-z]", self.value):
            raise ValueError("Password must contain at least one lowercase letter")
        if not re.search(r"[A-Z]", self.value):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"\d", self.value):
            raise ValueError("Password must contain at least one digit")
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", self.value):
            raise ValueError("Password must contain at least one special character")

    def __str__(self) -> str:
        return "********"  # Do not show the password

    def __eq__(self, other) -> bool:
        if not isinstance(other, Password):
            return False
        return self.value == other.value

    def __hash__(self) -> int:
        return hash(self.value)
