import typing as T

from ..domain.models import ShortURL


class ICodeGenerator(T.Protocol):
    def generate(self) -> str: ...


class ICodeRepository(T.Protocol):
    async def pop_unused(self) -> str | None: ...


class IURLRepository(T.Protocol):
    async def add(self, short_url: ShortURL) -> None: ...
    async def get_by_short_code(self, code: str) -> ShortURL | None: ...


class IUOW(T.Protocol):
    codes: ICodeRepository
    urls: IURLRepository

    async def __aenter__(self) -> T.Self: ...
    async def __aexit__(self, *args: T.Any) -> None: ...
