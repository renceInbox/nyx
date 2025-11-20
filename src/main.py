import asyncio

from advanced_alchemy.extensions.litestar import (
    SQLAlchemyPlugin,
)
from litestar import Litestar
from litestar.di import Provide

from config.db import alchemy_config
from src.dependencies import provide_limit_offset_pagination
from src.profiles.controllers import ProfileController
from src.utils import refresh_jwks_periodically


async def on_startup():
    asyncio.create_task(refresh_jwks_periodically())


app = Litestar(
    route_handlers=[ProfileController],
    plugins=[SQLAlchemyPlugin(config=alchemy_config)],
    dependencies={"limit_offset": Provide(provide_limit_offset_pagination)},
    on_startup=[on_startup],
)
