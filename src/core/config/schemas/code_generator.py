from pydantic_settings import BaseSettings


class CodeGenerator(BaseSettings):
    TARGET_UNUSED_STORED_CODES: int
    BATCH_SIZE: int
