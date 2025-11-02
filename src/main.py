from advanced_alchemy.extensions.litestar import (
    SQLAlchemyPlugin,
)
from litestar import Litestar
from litestar.di import Provide

from config.db import alchemy_config
from src.dependencies import provide_limit_offset_pagination
from src.profiles.endpoints import ProfileController

app = Litestar(
    route_handlers=[ProfileController],
    plugins=[SQLAlchemyPlugin(config=alchemy_config)],
    dependencies={"limit_offset": Provide(provide_limit_offset_pagination)},
)
