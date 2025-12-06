from typing import Annotated
from typing import Generic, TypeVar

import msgspec
from msgspec import Meta

PositiveIntStruct = Annotated[int, Meta(gt=0)]
EmailStrStruct = Annotated[
    str, Meta(pattern=r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
]


T = TypeVar("T")


class OffsetPagination(msgspec.Struct, Generic[T]):
    items: list[T]
    limit: int
    offset: int
    total: int


class CurrentUser(msgspec.Struct):
    sub: str
    email: str | None = None
    preferred_username: str | None = None
    roles: list[str] = msgspec.field(default_factory=list)
    exp: int | None = None
