import asyncio
import logging
import traceback

from aioclock import AioClock, Every

from ...service.event_processor import event_processor
from ...infrastructure import UOW as OutboxUOW

from src.modules.shared.constants.domain_event_ctx import DomainEventCtx
from src.modules.url_shortener.infrastructure import UOW as URLShortenerUOW


logger = logging.getLogger(__name__)

app = AioClock()


@app.task(trigger=Every(seconds=1))  # type: ignore
async def process_events() -> None:
    ctx = DomainEventCtx(url_uow=URLShortenerUOW(), outbox_uow=OutboxUOW())
    try:
        await event_processor(ctx)
    except Exception:
        logger.critical(traceback.format_exc())


if __name__ == "__main__":
    asyncio.run(app.serve())
