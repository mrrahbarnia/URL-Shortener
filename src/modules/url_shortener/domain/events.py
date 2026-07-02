from dataclasses import dataclass

from . import value_objects

from src.modules.shared.constants import DomainEvent


@dataclass(frozen=True)
class LinkVisited(DomainEvent):
    url_id: value_objects.ShortURLID
    original_url: str
    short_code: str
