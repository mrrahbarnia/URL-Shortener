import logging
import typing as T
from collections import defaultdict

from src.modules.shared.constants import DomainEvent, DOMAIN_EVENT_REGISTRY
from src.modules.shared.constants.domain_event_ctx import DomainEventCtx

logger = logging.getLogger(__name__)

EVENT_HANDLERS: dict[
    str, list[T.Callable[[DomainEvent, DomainEventCtx], T.Awaitable[None] | None]]
] = defaultdict(list)


EventT = T.TypeVar("EventT", bound=DomainEvent)

AsyncHandlerType = T.Callable[[EventT, DomainEventCtx], T.Awaitable[None]]
SyncHandlerType = T.Callable[[EventT, DomainEventCtx], None]
HandlerType = AsyncHandlerType[EventT] | SyncHandlerType[EventT]


def handler_register(
    event_type: type[EventT],
) -> T.Callable[[HandlerType[EventT]], HandlerType[EventT]]:
    def decorator(fn: HandlerType[EventT]) -> HandlerType[EventT]:
        event_name_string = event_type.__name__
        EVENT_HANDLERS[event_name_string].append(fn)  # type: ignore[arg-type]
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
