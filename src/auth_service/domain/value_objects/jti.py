import re
from dataclasses import dataclass
from re import Pattern
from typing import ClassVar


@dataclass(frozen=True)
class JTI:
    value: str

    _uuid4_pattern: ClassVar[str] = (
        r"^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$"
    )
    _compiled_pattern: ClassVar[Pattern[str]] = None  # type: ignore

    @classmethod
    def _get_pattern(cls) -> Pattern[str]:
        if cls._compiled_pattern is None:
            cls._compiled_pattern = re.compile(cls._uuid4_pattern, re.IGNORECASE)
        return cls._compiled_pattern

    def __post_init__(self) -> None:
        if not isinstance(self.value, str):
            raise ValueError("JTI must be a string")
        if not self._get_pattern().match(self.value):
            raise ValueError("JTI must be a valid UUID4")

    def __str__(self) -> str:
        return self.value

    def __eq__(self, other) -> bool:
        if not isinstance(other, JTI):
            return False
        return self.value.lower() == other.value.lower()

    def __hash__(self) -> int:
        return hash(self.value.lower())
