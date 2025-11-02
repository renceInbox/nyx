from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".envs/.local", extra="ignore", case_sensitive=False
    )

    debug: bool = Field(default=False)
    sqlalchemy_database_uri: str = Field(
        default="postgresql+asyncpg://baseuser:password@localhost:5432/nyx"
    )


setting = Settings()
