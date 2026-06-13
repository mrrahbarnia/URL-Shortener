from dataclasses import dataclass

from src.modules.shared.constants import DomainEvent


@dataclass(frozen=True)
class LinkVisited(DomainEvent):
    short_code: str
