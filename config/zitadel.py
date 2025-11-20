from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".envs/.zitadel", extra="ignore", case_sensitive=False
    )

    issuer: str = Field(default="http://localhost:8080")
    jwks_url: str = Field(default="http://localhost:8080/oauth/v2/keys")
    audience: str = Field(default="347527518753980419")
    jwks_refresh_interval: int = Field(default=6 * 3600)


zitadel_settings = Settings()
