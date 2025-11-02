from advanced_alchemy.repository import SQLAlchemyAsyncRepository

from src.profiles.models import Profile


class ProfileRepository(SQLAlchemyAsyncRepository[Profile]):
    """Profile repository."""

    model_type = Profile
