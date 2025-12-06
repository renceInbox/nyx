import asyncio

from advanced_alchemy.extensions.litestar import (
    SQLAlchemyPlugin,
)
from litestar import Litestar
from litestar.openapi import OpenAPIConfig

from config.db import alchemy_config
from src.profiles.controllers import ProfileController
from src.utils import refresh_jwks_periodically


async def on_startup():
    asyncio.create_task(refresh_jwks_periodically())


openapi_config = OpenAPIConfig(
    title="Nyx API",
    version="1.0.0",
)


app = Litestar(
    route_handlers=[ProfileController],
    plugins=[SQLAlchemyPlugin(config=alchemy_config)],
    openapi_config=openapi_config,
    on_startup=[on_startup],
    # security=[oauth2_auth],
)
