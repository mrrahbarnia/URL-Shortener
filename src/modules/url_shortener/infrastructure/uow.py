import typing as T

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from ..infrastructure.repository import URLRepository, CodeRepository

from src.modules.events.infrastructure.repository import OutboxRepository
from src.modules.shared.infrastructure.db_metadata import SESSION_MAKER


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

        self.session = session
        return self

    async def __aexit__(
        self, exc_type: type[BaseException] | None, *args: T.Any
    ) -> None:
        try:
            if exc_type is not None:
                await self.rollback()
            else:
                await self.commit()
        finally:
            await self.session.close()

    async def rollback(self) -> None:
        await self.session.rollback()
        return None

    async def commit(self) -> None:
        await self.session.commit()
        return None
