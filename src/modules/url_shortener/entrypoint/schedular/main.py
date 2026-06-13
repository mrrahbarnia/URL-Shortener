import asyncio
import typing as T
import logging
import traceback

from aioclock import AioClock, Every, Depends

from .dependencies import get_uow, get_code_generator
from ...service.code_batch_generator import CodeBatchGenerator
from ...infrastructure import CodeGenerator, UOW


logger = logging.getLogger(__name__)

app = AioClock()


@app.task(trigger=Every(hours=1))  # type: ignore
async def refill_code_pool(
    uow: T.Annotated[UOW, Depends(get_uow)],
    code_generator: T.Annotated[CodeGenerator, Depends(get_code_generator)],
) -> None:
    try:
        await CodeBatchGenerator(uow, code_generator).refill_code_storage()
    except Exception:
        logger.critical(traceback.format_exc())


if __name__ == "__main__":
    asyncio.run(app.serve())
