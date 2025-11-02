from typing import Annotated

from msgspec import Meta

PositiveIntStruct = Annotated[int, Meta(gt=0)]
EmailStrStruct = Annotated[str, Meta(pattern=r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")]
