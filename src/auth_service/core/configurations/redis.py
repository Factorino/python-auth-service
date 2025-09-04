from pydantic import Field, computed_field
from pydantic_settings import SettingsConfigDict

from auth_service.core.configurations import BaseConfig


class RedisConfig(BaseConfig):
    host: str = Field(default="localhost")
    port: int = Field(default=6379)
    db: int = Field(default=0)

    @computed_field
    @property
    def dsn(self) -> str:
        return f"redis://{self.host}:{self.port}/{self.db}"

    model_config = SettingsConfigDict(env_prefix="REDIS_")
