import typing as T
from datetime import datetime, timezone

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession

from ..db_models import Outbox

from src.modules.shared.constants import DBLock


class OutboxRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def add(self, event_type: str, payload: dict[str, T.Any]) -> None:
        stmt = sa.insert(Outbox).values(
            {Outbox.event_type: event_type, Outbox.payload: payload}
        )
        await self.session.execute(stmt)

    async def fetch_unprocessed(
        self, limit: int, lock: DBLock = DBLock(is_active=False)
    ) -> T.Sequence[Outbox]:
        stmt = (
            sa.select(Outbox)
            .where(
                sa.and_(
                    Outbox.is_processed.is_(False),
                    Outbox.processing_error.is_(None),
                    Outbox.next_retry_at < datetime.now(timezone.utc),
                )
            )
            .limit(limit)
        )
        if lock.is_active:
            await self.session.execute(
                sa.text(f"SET LOCAL lock_timeout = '{lock.timeout_second}s'")
            )
            stmt = stmt.with_for_update(skip_locked=lock.skip_locked)

        try:
            return (await self.session.scalars(stmt)).all()
        except Exception:
            return []

    async def mark_processed(self, id: int) -> None:
        stmt = (
            sa.update(Outbox)
            .values({Outbox.is_processed: True, Outbox.processed_at: datetime.now()})
            .where(Outbox.id == id)
        )
        await self.session.execute(stmt)

    async def get_by_id(
        self, id: int, lock: DBLock = DBLock(is_active=False)
    ) -> Outbox | None:
        stmt = sa.select(Outbox).where(Outbox.id == id).limit(1)
        if lock.is_active:
            await self.session.execute(
                sa.text(f"SET LOCAL lock_timeout = '{lock.timeout_second}s'")
            )
            stmt = stmt.with_for_update(skip_locked=lock.skip_locked)
        try:
            event = await self.session.scalar(stmt)
            return event
        except Exception:
            return None

    async def schedule_retry(self, id: int, next_retry_at: datetime) -> None:
        stmt = (
            sa.update(Outbox)
            .values(
                {
                    Outbox.retry_attempt: Outbox.retry_attempt + 1,
                    Outbox.next_retry_at: next_retry_at,
                    Outbox.last_attempted_at: datetime.now(),
                }
            )
            .where(Outbox.id == id)
        )
        await self.session.execute(stmt)

    async def mark_dead(self, id: int, processing_error: str) -> None:
        stmt = (
            sa.update(Outbox)
            .values(
                {
                    Outbox.processing_error: processing_error,
                    Outbox.retry_attempt: Outbox.retry_attempt + 1,
                    Outbox.last_attempted_at: datetime.now(),
                }
            )
            .where(Outbox.id == id)
        )
        await self.session.execute(stmt)
