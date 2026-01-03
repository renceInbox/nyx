from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".envs/.env.zitadel", extra="ignore", case_sensitive=False
    )

    issuer: str = Field(default="http://localhost:8080")
    jwks_url: str = Field(default="http://localhost:8080/oauth/v2/keys")
    audience: str = Field(default="client-id")
    client_id: str = Field(default="client-id")
    client_secret: str | None = Field(default=None)
    key_id: str | None = Field(default=None)
    jwks_refresh_interval: int = Field(default=6 * 3600)
    jwt_secret: str = Field(default="secret")
    use_introspection: bool = Field(default=False)

    web_client_id: str = Field(default="client-id-fe")
    web_client_secret: str = Field(default="secret")
    web_redirect_uri: str = Field(default="http://localhost:8000/callback")
    authorization_endpoint: str = Field(default="/oauth/v2/auth")
    token_endpoint: str = Field(default="/oauth/v2/token")


zitadel_settings = Settings()
