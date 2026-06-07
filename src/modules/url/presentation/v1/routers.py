import typing as T

from fastapi import APIRouter, status, Depends

from . import dtos
from .dependencies import get_uow, get_code_generator
from ...service import commands
from ...infrastructure.uow import UOW
from ...infrastructure.code_generator import ICodeGenerator

router = APIRouter(prefix="/url")


@router.post("/shorten", status_code=status.HTTP_201_CREATED)
async def shorten_link(
    payload: dtos.ShortenURLRequest,
    uow: T.Annotated[UOW, Depends(get_uow)],
    code_generator: T.Annotated[ICodeGenerator, Depends(get_code_generator)],
) -> str:
    try:
        cmd = commands.ShortURLCommand(
            url=str(payload.original_url), expires_at=payload.expires_at
        )
        await commands.URLCommandHandler(uow).shorten_url(
            code_generator=code_generator, command=cmd
        )
        return "OK"
    except Exception as ex:
        print("===================== Printing")
        print(ex)
        raise
