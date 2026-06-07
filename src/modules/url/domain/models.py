from dataclasses import dataclass, field
from datetime import UTC, datetime
from uuid import UUID, uuid4

from src.modules.shared.constants import DomainError, DomainEvent

from .events import URLResolved
from .value_objects import URL, ShortCode


class LinkExpired(DomainError):
    def __init__(self, message: str) -> None:
        super().__init__(message)


@dataclass
class ShortURL:
    id: UUID = field(default_factory=uuid4, init=False)
    original_url: URL
    short_code: ShortCode
    created_at: datetime
    expires_at: datetime | None = None

    _events: list[DomainEvent] = field(default_factory=list, init=False)

    def resolve(self) -> URL:
        if self.is_expired():
            raise LinkExpired(message="Link expired")

        self._events.append(URLResolved(id=self.id))

        return self.original_url

    def is_expired(self) -> bool:
        if self.expires_at is None:
            return False
        
        return datetime.now(UTC) >= self.expires_at
    