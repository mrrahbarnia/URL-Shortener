import re
from dataclasses import dataclass
from urllib.parse import urlparse

from src.modules.shared.constants import DomainError


class InvalidURL(DomainError):
    def __init__(self, message: str) -> None:
        super().__init__(message)


@dataclass(frozen=True)
class URL:
    value: str

    def __post_init__(self) -> None:
        # TODO - We can use Regex for validation

        parsed_url = urlparse(url=self.value)

        if not parsed_url.scheme:
            raise InvalidURL(message="URL must containt schema")
        
        if not parsed_url.netloc:
            raise InvalidURL(message="URL must contain host")
        

class InvalidShortCode(DomainError):
    def __init__(self, message: str) -> None:
        super().__init__(message)

SHORT_CODE_REGEX = r'^[A-Za-z0-9]{7}$'

@dataclass(frozen=True)
class ShortCode:
    value: str

    _pattern = re.compile(SHORT_CODE_REGEX)

    def __post_init__(self) -> None:
        if not self._pattern.match(self.value):
            raise InvalidShortCode(message="Short code must be alphanumeric and also 7 length")
