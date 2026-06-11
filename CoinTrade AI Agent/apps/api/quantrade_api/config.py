from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env.local", env_prefix="QUANTRADE_")

    mode: str = Field(default="fixture", pattern="^(fixture|live|test)$")
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    cors_origins: str = "http://localhost:5173"
    database_url: str = "sqlite:///./quantrade.db"
    redis_url: str = "redis://localhost:6379/0"
    dev_auth_enabled: bool = True


settings = Settings()

