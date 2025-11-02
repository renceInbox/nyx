from advanced_alchemy import filters
from advanced_alchemy.exceptions import NotFoundError
from advanced_alchemy.service import OffsetPagination
from litestar import Controller, get, post, patch, delete
from litestar.di import Provide
from litestar.exceptions import HTTPException
from litestar.params import Parameter

from src.profiles.dependencies import provide_profiles_service
from src.profiles.schemas import (
    ProfileStruct,
    ProfileWriteStruct,
    ProfileWriteDTO,
    ProfileDTO,
)
from src.profiles.services import ProfileService


class ProfileController(Controller):
    """Profile CRUD"""

    dependencies = {"service": Provide(provide_profiles_service)}
    dto = ProfileWriteDTO
    return_dto = ProfileDTO

    @get(path="/profiles")
    async def list_profiles(
        self,
        service: ProfileService,
        limit_offset: filters.LimitOffset,
    ) -> OffsetPagination[ProfileStruct]:
        """
        Handles retrieving a paginated list of profiles using the provided filtering and
        pagination parameters.

        :param service: The service responsible for fetching and managing profile data.
                        Must implement methods to list and count profiles.
        :type service: ProfileService
        :param limit_offset: Object containing pagination parameters, including `limit` and
                             `offset`.
        :type limit_offset: filters.LimitOffset
        :return: An OffsetPagination object containing the list of profiles, the total
                 count, and pagination metadata (limit and offset).
        :rtype: OffsetPagination[ProfileStruct]
        """
        results, total = await service.list_and_count(limit_offset)
        return OffsetPagination[ProfileStruct](
            items=results,
            total=total,
            limit=limit_offset.limit,
            offset=limit_offset.offset,
        )

    @post(path="/profiles")
    async def create_profile(
        self,
        service: ProfileService,
        data: ProfileWriteStruct,
    ) -> ProfileStruct:
        """
        Creates a user profile using the provided service and data.

        :param service: An instance of ProfileService used to handle profile creation.
        :type service: ProfileService
        :param data: The input data required to create the profile.
        :type data: ProfileWriteStruct
        :return: The created profile object.
        :rtype: ProfileStruct
        """
        return await service.create(data, auto_commit=True)

    @get(path="/profiles/{profile_id:int}")
    async def get_profile(
        self,
        service: ProfileService,
        profile_id: int = Parameter(
            title="ProfileSchema ID",
            description="The ProfileSchema to retrieve.",
        ),
    ) -> ProfileStruct:
        """
        Retrieves a profile by the given profile ID.

        This endpoint fetches a profile associated with the provided profile ID
        using the service instance. If no profile is found for the given ID,
        a 404 HTTP exception is raised.

        :param service: Instance of ProfileService used to process the request.
        :param profile_id: An integer identifier representing the profile to retrieve.
        :return: A ProfileStruct instance reflecting the requested profile data.
        """
        try:
            return await service.get(profile_id)
        except NotFoundError:
            raise HTTPException(
                detail="No profile found.",
                status_code=404,
            )

    @patch(
        path="/profiles/{profile_id:int}",
    )
    async def update_profile(
        self,
        service: ProfileService,
        data: ProfileWriteStruct,
        profile_id: int = Parameter(
            title="ProfileSchema ID",
            description="The ProfileSchema to update.",
        ),
    ) -> ProfileStruct:
        """
        Updates a profile with the given data.

        This function updates an existing profile identified by the given `profile_id`
        using the provided `data`. The `service` parameter is used to handle the
        updating operation asynchronously.

        :param service: The ProfileService instance responsible for managing profiles.
        :param data: An instance of ProfileWriteStruct containing the update data.
        :param profile_id: The ID of the profile to be updated.
        :return: An updated ProfileStruct object.
        """
        return await service.update(data=data, item_id=profile_id, auto_commit=True)

    @delete(path="/profiles/{profile_id:int}")
    async def delete_profile(
        self,
        service: ProfileService,
        profile_id: int = Parameter(
            title="ProfileSchema ID",
            description="The ProfileSchema to delete.",
        ),
    ) -> None:
        """
        Deletes a profile associated with the given profile ID.

        This functionality allows the deletion of a specific profile through the
        provided service using the profile ID.

        :param service: The service instance that performs profile deletion.
        :type service: ProfileService
        :param profile_id: The unique identifier of the profile to delete.
        :type profile_id: int
        :return: None
        """
        await service.delete(profile_id)
