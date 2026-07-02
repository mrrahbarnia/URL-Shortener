from dataclasses import dataclass, field
from datetime import UTC, datetime
from uuid import UUID

from . import value_objects
from .events import LinkVisited

from src.modules.shared.constants import Entity, DomainError, DomainEvent


class LinkExpired(DomainError):
    def __init__(self, message: str) -> None:
        super().__init__(message)


@dataclass
class ShortURL(Entity):
    id: value_objects.ShortURLID
    original_url: value_objects.URL
    short_code: value_objects.ShortCode
    expires_at: datetime

    events: list[DomainEvent] = field(
        default_factory=lambda: list(), init=False, hash=False
    )

    def resolve(self) -> value_objects.URL:
        if self.is_expired():
            raise LinkExpired(message="Link expired")

        return self.original_url

    def rgister_click(self) -> None:
        self.events.append(
            LinkVisited(
                url_id=self.id,
                original_url=self.original_url.value,
                short_code=self.short_code.value,
            )
        )

    def is_expired(self) -> bool:
        return datetime.now(UTC) >= self.expires_at

    @classmethod
    def create(
        cls, id: UUID, original_url: str, short_code: str, expires_at: datetime
    ) -> "ShortURL":
        if expires_at < datetime.now(UTC):
            raise DomainError(message="expies_at cannot be in past")

        return ShortURL(
            id=value_objects.ShortURLID(id),
            original_url=value_objects.URL(original_url),
            short_code=value_objects.ShortCode(short_code),
            expires_at=expires_at,
        )
