import typing as T
import sqlalchemy as sa

from sqlalchemy.ext.asyncio import AsyncSession

from . import models as db_models
from ...domain import models as domain_models


class CodeRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

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
            }
        )
        await self.session.execute(stmt)

    async def get_by_short_code(self, code: str) -> domain_models.ShortURL | None: ...
