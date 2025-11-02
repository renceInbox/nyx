from advanced_alchemy.extensions.litestar import (
    AsyncSessionConfig,
    SQLAlchemyAsyncConfig,
)

from config.base import setting
from src.profiles.models import Profile  # noqa

alchemy_config = SQLAlchemyAsyncConfig(
    connection_string=setting.sqlalchemy_database_uri,
    before_send_handler="autocommit",
    session_config=AsyncSessionConfig(expire_on_commit=False),
)
