from dataclasses import dataclass


@dataclass(frozen=True)
class UserId:
    value: int

    def __post_init__(self) -> None:
        if not isinstance(self.value, int):
            raise ValueError("UserId must be an integer")
        if self.value <= 0:
            raise ValueError("UserId must be a positive number")

    def __int__(self) -> int:
        return self.value

    def __eq__(self, other) -> bool:
        if not isinstance(other, UserId):
            return False
        return self.value == other.value

    def __hash__(self) -> int:
        return hash(self.value)
