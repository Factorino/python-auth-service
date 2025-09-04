from functools import lru_cache

from auth_service.core.configurations import (
    AppConfig,
    BaseConfig,
    DatabaseConfig,
    JWTConfig,
    RedisConfig,
)


class Config(BaseConfig):
    app = AppConfig()
    database = DatabaseConfig()
    redis = RedisConfig()
    jwt = JWTConfig()  # type: ignore


@lru_cache(maxsize=1)
def load_config() -> Config:
    return Config()
