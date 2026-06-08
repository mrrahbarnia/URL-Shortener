import typing as T
import sqlalchemy as sa

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import insert as upsert
from src.modules.shared.constants import DBLock

from . import models as db_models
from ...domain import value_objects
from ...domain import models as domain_models


class CodeRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def count_unused(self) -> int:
        stmt = sa.select(sa.func.count()).where(db_models.CODE.is_used.is_(False))
        unused_count = await self.session.scalar(stmt)
        return unused_count if unused_count else 0

    async def bulk_insert_unused(self, codes: set[str]) -> int:
        values = [{db_models.CODE.code: code} for code in codes]
        stmt = (
            upsert(db_models.CODE)
            .values(values)
            .on_conflict_do_nothing()
            .returning(db_models.CODE.code)
        )
        return len((await self.session.scalars(stmt)).all())

    async def pop_unused(self) -> str | None:
        cte = (
            sa.select(db_models.CODE.code)
            .where(db_models.CODE.is_used.is_(False))
            .limit(1)
            .with_for_update(skip_locked=True)
            .cte()
        )

        update_stmt = (
            sa.update(db_models.CODE)
            .values({db_models.CODE.is_used: True})
            .where(db_models.CODE.code == sa.select(cte.c.code))
            .returning(db_models.CODE.code)
        )

        row = await self.session.scalar(update_stmt)
        return row


class URLRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self._seen: T.Set[domain_models.ShortURL] = set()

    async def add(self, domain_url: domain_models.ShortURL) -> None:
        stmt = sa.insert(db_models.URL).values(
            {
                db_models.URL.id: domain_url.id,
                db_models.URL.short_code: domain_url.short_code.value,
                db_models.URL.original_url: domain_url.original_url.value,
                db_models.URL.expires_at: domain_url.expires_at,
            }
        )
        await self.session.execute(stmt)

    async def get_by_short_code(
        self, short_code: str, lock: DBLock = DBLock(is_active=False)
    ) -> domain_models.ShortURL | None:
        stmt = (
            sa.select(db_models.URL)
            .where(db_models.URL.short_code == short_code)
            .limit(1)
        )

        if lock.is_active:
            await self.session.execute(
                sa.text(f"SET LOCAL lock_timeout = '{lock.timeout_second}s'")
            )
            stmt = stmt.with_for_update(skip_locked=lock.skip_locked)

        try:
            db_url = await self.session.scalar(stmt)
            if db_url is None:
                return None

            return domain_models.ShortURL(
                id=db_url.id,
                original_url=value_objects.URL(db_url.original_url),
                short_code=value_objects.ShortCode(db_url.short_code),
                created_at=db_url.created_at,
                expires_at=db_url.expires_at,
            )
        except Exception:
            return None
