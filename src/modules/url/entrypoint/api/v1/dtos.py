from datetime import datetime, UTC

from pydantic import BaseModel, HttpUrl, field_validator

from ....domain.value_objects import ShortURLID


class ShortenURLRequest(BaseModel):
    # TODO - It's better to use Regex for original_url validation
    original_url: HttpUrl
    expires_at: datetime | None = None

    @field_validator("expires_at")
    @classmethod
    def ensure_expires_at_in_future(cls, value: datetime) -> datetime:
        if value < datetime.now(UTC):
            raise ValueError("expires_at field cannot be in past")
        return value


class ShortenURLResponse(BaseModel):
    id: ShortURLID
    original_url: str
    short_code: str
    expires_at: datetime | None = None


class VisitURLResponse(BaseModel):
    original_url: str
