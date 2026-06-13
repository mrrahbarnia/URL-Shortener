from pydantic_settings import BaseSettings


class OutboxConsumer(BaseSettings):
    MAX_RETRIES: int
    BACKOFF_SEC: int
