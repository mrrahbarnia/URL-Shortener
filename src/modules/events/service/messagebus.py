import logging
import typing as T
from collections import defaultdict

from src.modules.shared.constants import DomainEvent, DOMAIN_EVENT_REGISTRY
from src.modules.shared.constants.domain_event_ctx import DomainEventCtx

logger = logging.getLogger(__name__)

EVENT_HANDLERS: dict[
    str, list[T.Callable[[DomainEvent, DomainEventCtx], T.Awaitable[None] | None]]
] = defaultdict(list)

AsyncHandlerType = T.Callable[[DomainEvent, DomainEventCtx], T.Awaitable[None]]
SyncHandlerType = T.Callable[[DomainEvent, DomainEventCtx], None]
HandlerType = AsyncHandlerType | SyncHandlerType


def handler_register(
    event_type: type[DomainEvent],
) -> T.Callable[[HandlerType], HandlerType]:
    def decorator(fn: HandlerType) -> HandlerType:
        event_name_string = event_type.__name__
        EVENT_HANDLERS[event_name_string].append(fn)

        return fn

    return decorator


async def handle_event(
    event_type: str, payload: dict[str, T.Any], ctx: DomainEventCtx
) -> None:
    handlers = EVENT_HANDLERS.get(event_type, [])

    event_cls = DOMAIN_EVENT_REGISTRY.get(event_type)
    if not event_cls:
        logger.critical(
            f"Unknown event type: {event_type}",
            exc_info=True,
        )

        return

    event = event_cls(**payload)

    for handler in handlers:
        result = handler(event, ctx)
        if result is not None:
            await result
