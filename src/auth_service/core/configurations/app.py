from pydantic import Field
from pydantic_settings import SettingsConfigDict

from auth_service.core.configurations import BaseConfig


class AppConfig(BaseConfig):
    host: str = Field(default="0.0.0.0")
    port: int = Field(default=8000)
    debug: bool = Field(default=False)

    model_config = SettingsConfigDict(env_prefix="APP_")
