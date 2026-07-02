import json

from ..domain.events import LinkVisited

from src.core.config import ENVS
from src.modules.events.service.messagebus import handler_register
from src.modules.shared.constants.domain_event_ctx import DomainEventCtx


@handler_register(LinkVisited)
async def on_link_visited(event: LinkVisited, event_ctx: DomainEventCtx):
    try:
        await event_ctx.producer.send_message(
            topic=ENVS.KAFKA.URL_SHORTENER_TOPIC_NAME,
            key=None,
            value=json.dumps(event.to_dict()),
        )
    except Exception:
        raise
