import asyncio

from advanced_alchemy.extensions.litestar import (
    SQLAlchemyPlugin,
)
from litestar import Litestar
from litestar.di import Provide
from litestar.openapi import OpenAPIConfig
from litestar.openapi.spec import Components, SecurityScheme

from config.db import alchemy_config
from src.dependencies import provide_limit_offset_pagination
from src.profiles.controllers import ProfileController
from src.utils import refresh_jwks_periodically


async def on_startup():
    asyncio.create_task(refresh_jwks_periodically())


# Define Bearer security scheme
components = Components(
    security_schemes={
        "bearerAuth": SecurityScheme(
            type="http",
            scheme="bearer",
            bearer_format="Bearer",
            description="Enter your Bearer token",
        )
    }
)

openapi_config = OpenAPIConfig(
    title="Nyx API",
    version="1.0.0",
    components=components,
    security=[{"bearerAuth": []}],  # Apply globally
)


app = Litestar(
    route_handlers=[ProfileController],
    plugins=[SQLAlchemyPlugin(config=alchemy_config)],
    dependencies={"limit_offset": Provide(provide_limit_offset_pagination)},
    openapi_config=openapi_config,
    on_startup=[on_startup],
)
