from pydantic import Field
from pydantic_settings import SettingsConfigDict

from auth_service.core.configurations import BaseConfig


class JWTConfig(BaseConfig):
    secret_key: str
    algorithm: str = Field(default="HS256")
    access_token_expires_in: int = Field(default=3600)  # 1 hour
    refresh_token_expires_in: int = Field(default=604800)  # 7 days

    model_config = SettingsConfigDict(env_prefix="JWT_")
