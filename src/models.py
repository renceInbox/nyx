from advanced_alchemy.base import IdentityAuditBase
from advanced_alchemy.types import BigIntIdentity
from litestar.dto import dto_field
from sqlalchemy import Identity
from sqlalchemy.orm import declared_attr, Mapped, mapped_column


class BaseModel(IdentityAuditBase):

    @declared_attr
    def id(cls) ->  Mapped[int]:
        """Primary key column using IDENTITY."""
        return mapped_column(
            BigIntIdentity,
            Identity(start=1, increment=1),
            primary_key=True,
            sort_order=-100,
            info=dto_field("write-only")
        )
