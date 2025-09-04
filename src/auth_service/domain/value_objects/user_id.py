from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True, slots=True)
class UserID:
    value: UUID

    def __str__(self) -> str:
        return str(self.value)

    def __eq__(self, other) -> bool:
        if not isinstance(other, UserID):
            return False
        return self.value == other.value

    def __hash__(self) -> int:
        return hash(self.value)
