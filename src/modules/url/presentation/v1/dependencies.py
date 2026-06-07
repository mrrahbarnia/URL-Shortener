from ...infrastructure.uow import UOW
from ...infrastructure.code_generator import ICodeGenerator


async def get_uow() -> UOW:
    return UOW()


async def get_code_generator() -> ICodeGenerator:
    return ICodeGenerator()
