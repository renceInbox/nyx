from advanced_alchemy.service import SQLAlchemyAsyncRepositoryService

from src.profiles.models import Profile
from src.profiles.repositories import ProfileRepository


class ProfileService(SQLAlchemyAsyncRepositoryService[Profile, ProfileRepository]):
    """Service for managing blog Profiles with automatic schema validation."""

    repository_type = ProfileRepository
