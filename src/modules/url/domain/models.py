from dataclasses import dataclass, field
from datetime import UTC, datetime
from uuid import uuid4

from src.modules.shared.constants import DomainError, DomainEvent

from . import value_objects
from .events import LinkVisited


class LinkExpired(DomainError):
    def __init__(self, message: str) -> None:
        super().__init__(message)


@dataclass
class ShortURL:
    original_url: value_objects.URL
    short_code: value_objects.ShortCode
    created_at: datetime
    expires_at: datetime | None = None
    id: value_objects.ShortURLID = field(
        default_factory=lambda: value_objects.ShortURLID(uuid4())
    )

    _events: list[DomainEvent] = field(default_factory=lambda: list(), init=False)

    def resolve(self) -> value_objects.URL:
        if self.is_expired():
            raise LinkExpired(message="Link expired")

        return self.original_url

    def rgister_click(self) -> None:
        self._events.append(LinkVisited(short_code=self.short_code.value))

    def is_expired(self) -> bool:
        if self.expires_at is None:
            return False

        return datetime.now(UTC) >= self.expires_at

    @classmethod
    def create(
        cls, original_url: str, short_code: str, expires_at: datetime | None
    ) -> "ShortURL":
        if expires_at and expires_at < datetime.now(UTC):
            raise DomainError(message="expies_at cannot be in past")

        return ShortURL(
            original_url=value_objects.URL(original_url),
            short_code=value_objects.ShortCode(short_code),
            created_at=datetime.now(UTC),
            expires_at=expires_at,
        )
