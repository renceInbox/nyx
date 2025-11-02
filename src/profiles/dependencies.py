from sqlalchemy.ext.asyncio import AsyncSession

from src.profiles.services import ProfileService


async def provide_profiles_service(db_session: AsyncSession) -> ProfileService:
    """This provides the default Authors repository."""
    return ProfileService(session=db_session)
