from ...infrastructure import UOW as OutboxUOW

from src.modules.url_shortener.infrastructure import UOW as URLShortenerUOW
from src.modules.shared.constants.domain_event_ctx import DomainEventCtx


async def get_event_ctx() -> DomainEventCtx:
    return DomainEventCtx(url_uow=URLShortenerUOW(), outbox_uow=OutboxUOW())
