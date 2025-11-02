from advanced_alchemy.base import IdentityAuditBase
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column


class Profile(IdentityAuditBase):
    __tablename__ = "profiles"

    full_name: Mapped["str"] = mapped_column(String(100), nullable=False)
    email: Mapped["str"] = mapped_column(String(100), nullable=True)
