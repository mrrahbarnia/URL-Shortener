import logging
import typing as T
from contextlib import asynccontextmanager
from logging.config import dictConfig

from fastapi import FastAPI

from .logger import LogConfig

from src.modules.shared.infrastructure.kafka import PRODUCER, create_topics
from src.modules.events.service import bootstrap


logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_application: FastAPI) -> T.AsyncGenerator[None, None]:
    # ============================== On startup
    logger.info("Logger is running...")
    dictConfig(LogConfig().model_dump())

    logger.info("Kafka topics are creating...")
    create_topics()

    logger.info("Kafka producer is running...")
    await PRODUCER.start()

    logger.info("Bootstrapping event handlers...")
    bootstrap()

    logger.info("Application is running...")

    yield
    # ============================== On shutdown

    logger.info("Kafka producer is gracefully shutting down...")
    await PRODUCER.stop()

    logger.info("Application is shutting down...")
