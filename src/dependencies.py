from advanced_alchemy import filters
from litestar.connection import ASGIConnection
from litestar.exceptions import NotAuthorizedException
from litestar.params import Parameter

from src.schemas import CurrentUser


def provide_limit_offset_pagination(
    current_page: int = Parameter(ge=1, query="currentPage", default=1, required=False),
    page_size: int = Parameter(
        query="pageSize",
        ge=1,
        default=10,
        required=False,
    ),
) -> filters.LimitOffset:
    """Add offset/limit pagination.

    Return type consumed by `Repository.apply_limit_offset_pagination()`.

    Parameters
    ----------
    current_page : int
        LIMIT to apply to select.
    page_size : int
        OFFSET to apply to select.
    """
    return filters.LimitOffset(page_size, page_size * (current_page - 1))


async def get_current_user(connection: ASGIConnection) -> CurrentUser:
    if not hasattr(connection.state, "current_user"):
        raise NotAuthorizedException("Unauthorized")
    return connection.state.current_user
