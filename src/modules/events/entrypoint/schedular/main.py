import asyncio
import logging
import traceback

from aioclock import AioClock, Every

from ...service import bootstrap
from ...service.event_processor import event_processor
from ...infrastructure import UOW as OutboxUOW

from src.modules.shared.constants.domain_event_ctx import DomainEventCtx
from src.modules.shared.infrastructure.kafka import PRODUCER, create_topics
from src.modules.url_shortener.infrastructure import UOW as URLShortenerUOW


logger = logging.getLogger(__name__)

app = AioClock()


@app.task(trigger=Every(seconds=1))  # type: ignore
async def process_events() -> None:
    event_ctx = DomainEventCtx(
        url_uow=URLShortenerUOW(), outbox_uow=OutboxUOW(), producer=PRODUCER
    )
    try:
        await event_processor(event_ctx)
    except Exception:
        logger.critical(traceback.format_exc())


async def main() -> None:
    try:
        bootstrap()
    except Exception as ex:
        raise RuntimeError(f"Cannot bootstrap event handlers due to: {ex}")

    try:
        create_topics()
    except Exception as ex:
        raise RuntimeError(f"Cannot create kafka topics due to: {ex}")

    try:
        await PRODUCER.start()
    except Exception as ex:
        raise RuntimeError(f"Cannot create kafka topics due to: {ex}")

    await app.serve()


if __name__ == "__main__":
    asyncio.run(main())
