from ..domain.events import LinkVisited

from src.modules.events.service.messagebus import handler_register
from src.modules.shared.constants.domain_event_ctx import DomainEventCtx


@handler_register(LinkVisited)
async def on_link_visited(event: LinkVisited, event_ctx: DomainEventCtx):
    try:
        await event_ctx.producer.send_message(
            topic="url-shortener.link.visited", key=None, value=event.short_code
        )
    except Exception:
        raise
