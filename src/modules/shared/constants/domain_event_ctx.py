from dataclasses import dataclass

from ..infrastructure.kafka import KafkaProducer

from src.modules.url_shortener.service.interfaces import IUOW as IURLShortenerUOW
from src.modules.events.service.interfaces import IUOW as IOutboxUOW


@dataclass(frozen=True)
class DomainEventCtx:
    producer: KafkaProducer
    url_uow: IURLShortenerUOW
    outbox_uow: IOutboxUOW
