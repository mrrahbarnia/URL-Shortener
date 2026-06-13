import typing as T
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from .repository import OutboxRepository

from src.modules.shared.infrastructure.db_metadata import SESSION_MAKER


class UOW:
    def __init__(
        self,
        session_maker: async_sessionmaker[AsyncSession] = SESSION_MAKER,
    ) -> None:
        self.session_maker = session_maker
        self._outbox: OutboxRepository | None = None

    @property
    def outbox(self) -> OutboxRepository:
        if self._outbox is None:
            raise RuntimeError("UOW not entered")
        return self._outbox

    async def __aenter__(self) -> T.Self:
        session = self.session_maker()

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
                await self.commit()
        finally:
            await self.session.close()

    async def rollback(self) -> None:
        await self.session.rollback()
        return None

    async def commit(self) -> None:
        await self.session.commit()
        return None
