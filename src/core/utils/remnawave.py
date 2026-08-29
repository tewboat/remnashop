from typing import TypeVar, cast

from httpx import Response
from pydantic import BaseModel

RemnawaveResponseT = TypeVar("RemnawaveResponseT", bound=BaseModel)


def validate_remnawave_response(
    response: RemnawaveResponseT | str | bytes | Response,
) -> RemnawaveResponseT:
    if isinstance(response, BaseModel):
        return cast(RemnawaveResponseT, response)

    raise TypeError(
        "Unexpected response from Remnawave API: "
        f"expected a response DTO, got {type(response).__name__}"
    )
