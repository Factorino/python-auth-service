from dataclasses import dataclass
from typing import Dict


@dataclass(frozen=True)
class TokenPair:
    access_token: str
    refresh_token: str

    def to_dict(self) -> Dict[str, str]:
        return {
            "access_token": self.access_token,
            "refresh_token": self.refresh_token,
            "token_type": "bearer",
        }
