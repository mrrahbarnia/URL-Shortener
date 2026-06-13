from pydantic_settings import BaseSettings, SettingsConfigDict

from . import schemas
from src.modules.shared.constants import Environment


class _ENVS(BaseSettings):
    model_config = SettingsConfigDict(
        env_nested_delimiter="__",
        env_file=".env",
    )
    ENVIRONMENT: Environment
    POSTGRESQL: schemas.PostgreSQL
    FASTAPI: schemas.FastAPI
    CONSTANT: schemas.Constant
    CODE_GENERATOR: schemas.CodeGenerator
    OUTBOX_CONSUMER: schemas.OutboxConsumer


ENVS = _ENVS()  # type: ignore
