import msgspec
from litestar.dto import DTOConfig

from src.schemas import PositiveIntStruct, EmailStrStruct
from litestar.dto.msgspec_dto import MsgspecDTO


class BaseProfileStruct(msgspec.Struct):
    full_name: str
    email: EmailStrStruct


class ProfileStruct(BaseProfileStruct):
    id: PositiveIntStruct | None = msgspec.field(default=None)


class ProfileWriteStruct(BaseProfileStruct):
    ...


class ProfileWriteDTO(MsgspecDTO[ProfileWriteStruct]):
    ...

class ProfileDTO(MsgspecDTO[ProfileStruct]):
    ...
