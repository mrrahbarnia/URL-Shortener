import typing as T

from src.core.config import ENVS

from ..domain.models import ShortURL


class ICodeGenerator(T.Protocol):
    def generate_code(self, length: int = ENVS.CONSTANT.SHORT_CODE_LENGTH) -> str: ...

    def encode_base62(self, num: int) -> str: ...


class ICodeRepository(T.Protocol):
    async def pop_unused(self) -> str | None: ...


class IURLRepository(T.Protocol):
    async def add(self, domain_url: ShortURL) -> None: ...
    async def get_by_short_code(self, code: str) -> ShortURL | None: ...


class IUOW(T.Protocol):
    @property
    def urls(self) -> IURLRepository: ...

    @property
    def codes(self) -> ICodeRepository: ...

    async def __aenter__(self) -> T.Self: ...
    async def __aexit__(
        self, exc_type: type[BaseException] | None, *args: T.Any
    ) -> None: ...
