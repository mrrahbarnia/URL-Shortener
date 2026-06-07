from dataclasses import dataclass
from uuid import UUID

from src.modules.shared.constants import DomainEvent


@dataclass(frozen=True)
class LinkVisited(DomainEvent):
    id: UUID
    