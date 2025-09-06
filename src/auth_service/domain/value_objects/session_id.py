from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True, slots=True)
class SessionID:
    value: UUID

    def __str__(self) -> str:
        return str(self.value)

    def __eq__(self, other) -> bool:
        if not isinstance(other, SessionID):
            return False
        return self.value == other.value

    def __hash__(self) -> int:
        return hash(self.value)

    @classmethod
    def from_string(cls, value: str) -> "SessionID":
        return cls(UUID(value))

    @classmethod
    def from_bytes(cls, value: bytes) -> "SessionID":
        return cls.from_string(value.decode())
