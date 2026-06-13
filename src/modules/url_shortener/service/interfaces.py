import typing as T

from ..domain.models import ShortURL

from src.core.config import ENVS
from src.modules.shared.constants import DBLock
from src.modules.events.service.interfaces import IOutboxRepository


class ICodeGenerator(T.Protocol):
    def generate_code(self, length: int = ENVS.CONSTANT.SHORT_CODE_LENGTH) -> str: ...
    def encode_base62(self, num: int) -> str: ...


class ICodeRepository(T.Protocol):
    async def pop_unused(self) -> str | None: ...
    async def count_unused(self) -> int: ...
    async def bulk_insert_unused(self, codes: set[str]) -> int:
        # bulk_insert_unused must return successfully inserted rows count
        ...


class IURLRepository(T.Protocol):
    async def add(self, domain_url: ShortURL, client_ip: str) -> None: ...
    async def get_by_short_code(
        self, short_code: str, lock: DBLock = DBLock(is_active=False)
    ) -> ShortURL | None: ...
    async def exist_not_expired_with_original_url_client_ip(
        self, original_url: str, client_ip: str
    ) -> ShortURL | None: ...


class IUOW(T.Protocol):
    @property
    def outbox(self) -> IOutboxRepository: ...

    @property
    def urls(self) -> IURLRepository: ...

    @property
    def codes(self) -> ICodeRepository: ...

    async def __aenter__(self) -> T.Self: ...
    async def __aexit__(
        self, exc_type: type[BaseException] | None, *args: T.Any
    ) -> None: ...
