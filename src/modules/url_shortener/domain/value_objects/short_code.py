import re
from dataclasses import dataclass

from src.core.config import ENVS
from src.modules.shared.constants import DomainError

SHORT_CODE_REGEX = rf"^[A-Za-z0-9]{{{ENVS.CONSTANT.SHORT_CODE_LENGTH}}}$"


class InvalidShortCode(DomainError):
    def __init__(self, message: str) -> None:
        super().__init__(message)


@dataclass(frozen=True)
class ShortCode:
    value: str

    _pattern = re.compile(SHORT_CODE_REGEX)

    def __post_init__(self) -> None:
        if not self._pattern.match(self.value):
            raise InvalidShortCode(
                message="Short code must be alphanumeric and also 7 length"
            )
