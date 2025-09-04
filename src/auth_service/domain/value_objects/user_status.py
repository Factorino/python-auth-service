# domain/value_objects/user_status.py
from enum import StrEnum


class UserStatus(StrEnum):
    ACTIVE = "active"
    BLOCKED = "blocked"
    PENDING = "pending"  # for future feature: email verification
