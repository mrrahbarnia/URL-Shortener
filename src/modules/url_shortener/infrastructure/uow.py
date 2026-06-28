import typing as T
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from ..infrastructure.repository import URLRepository, CodeRepository

from src.modules.events.infrastructure.repository import OutboxRepository
from src.modules.shared.constants import DomainEvent
from src.modules.shared.infrastructure.db_metadata import SESSION_MAKER


def serialize(value: T.Any) -> T.Any:
    if isinstance(value, UUID):
        return str(value)

    # asyncpg UUID fallback
    if value.__class__.__name__ == "UUID":
        return str(value)

    return value


def safe_to_dict(data: dict[str, T.Any]) -> dict[str, T.Any]:
    return {k: serialize(v) for k, v in data.items()}


class UOW:
    def __init__(
        self,
        session_maker: async_sessionmaker[AsyncSession] = SESSION_MAKER,
    ) -> None:
        self.session_maker = session_maker
        self._urls: URLRepository | None = None
        self._codes: CodeRepository | None = None
        self._outbox: OutboxRepository | None = None

    @property
    def outbox(self) -> OutboxRepository:
        if self._outbox is None:
            raise RuntimeError("UOW not entered")
        return self._outbox

    @property
    def urls(self) -> URLRepository:
        if self._urls is None:
            raise RuntimeError("UOW not entered")
        return self._urls

    @property
    def codes(self) -> CodeRepository:
        if self._codes is None:
            raise RuntimeError("UOW not entered")
        return self._codes

    async def __aenter__(self) -> T.Self:
        session = self.session_maker()

        self._urls = URLRepository(session)
        self._codes = CodeRepository(session)
        self._outbox = OutboxRepository(session)

        self.session = session
        return self

    async def __aexit__(
        self, exc_type: type[BaseException] | None, *args: T.Any
    ) -> None:
        try:
            if exc_type is not None:
                await self.rollback()
            else:
                await self.collect_new_events()
                await self.commit()
        finally:
            await self.session.close()

    async def collect_new_events(self) -> None:
        events: list[DomainEvent] = []

        for entity in self.urls.seen.values():
            while entity.events:
                events.append(entity.events.pop())

        for event in events:
            await self.outbox.add(
                event_type=event.__class__.__name__,
                payload=safe_to_dict(event.to_dict()),
            )

    async def rollback(self) -> None:
        await self.session.rollback()
        return None

    async def commit(self) -> None:
        await self.session.commit()
        return None
