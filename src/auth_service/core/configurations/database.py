from typing import Any, Dict

from pydantic import Field, computed_field
from pydantic_settings import SettingsConfigDict

from auth_service.core.configurations import BaseConfig


class DatabaseConfig(BaseConfig):
    host: str = Field(default="localhost")
    port: int = Field(default=5432)
    user: str = Field(default="postgres")
    password: str = Field(default="postgres")
    name: str = Field(default="postgres")
    driver: str = Field(default="postgresql+psycopg")

    pool_size: int = Field(default=10)
    max_overflow: int = Field(default=20)
    pool_timeout: int = Field(default=30)
    pool_recycle: int = Field(default=1800)
    echo: bool = Field(default=False)

    @property
    @computed_field
    def dsn(self) -> str:
        return (
            f"{self.driver}://{self.user}:{self.password}"
            f"@{self.host}:{self.port}/{self.name}"
        )

    @property
    @computed_field
    def engine_options(self) -> Dict[str, Any]:
        return {
            "pool_size": self.pool_size,
            "max_overflow": self.max_overflow,
            "pool_timeout": self.pool_timeout,
            "pool_recycle": self.pool_recycle,
            "echo": self.echo,
        }

    model_config = SettingsConfigDict(env_prefix="DB_")
