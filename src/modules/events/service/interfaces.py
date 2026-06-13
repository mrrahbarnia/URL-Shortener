import typing as T
from datetime import datetime

from ..infrastructure.db_models import Outbox

from src.modules.shared.constants import DBLock


class IOutboxRepository(T.Protocol):
    async def add(self, event_type: str, payload: dict[str, T.Any]) -> None: ...

    async def fetch_unprocessed(
        self, limit: int, lock: DBLock = DBLock(is_active=False)
    ) -> T.Sequence[Outbox]: ...

    async def mark_processed(self, id: int) -> None: ...

    async def get_by_id(
        self, id: int, lock: DBLock = DBLock(is_active=False)
    ) -> Outbox | None: ...

    async def schedule_retry(self, id: int, next_retry_at: datetime) -> None: ...

    async def mark_dead(self, id: int, processing_error: str) -> None: ...


class IUOW(T.Protocol):
    @property
    def outbox(self) -> IOutboxRepository: ...

    async def __aenter__(self) -> T.Self: ...
    async def __aexit__(
        self, exc_type: type[BaseException] | None, *args: T.Any
    ) -> None: ...
