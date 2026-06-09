import typing as T
import traceback
import logging

from fastapi import APIRouter, status, responses, Depends

from src.modules.shared.constants import DomainError
from src.modules.shared.entrypoint import AppBaseException

from . import dtos
from .exceptions import ServerError, BadRequestException
from .exception_mapper import handle_service_errors
from .response import HTTPResponse
from .dependencies import get_uow, get_code_generator
from ....service import commands
from ....infrastructure.uow import UOW
from ....infrastructure.code_generator import CodeGenerator

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/url")


@router.post("/shorten", status_code=status.HTTP_201_CREATED)
async def shorten_link(
    payload: dtos.ShortenURLRequest,
    uow: T.Annotated[UOW, Depends(get_uow)],
    code_generator: T.Annotated[CodeGenerator, Depends(get_code_generator)],
) -> HTTPResponse[dtos.ShortenURLResponse]:
    try:
        cmd = commands.ShortURLCommand(
            url=str(payload.original_url), expires_at=payload.expires_at
        )
        service_result = await commands.URLCommandHandler(uow).shorten_url(
            code_generator=code_generator, cmd=cmd
        )
        short_url = handle_service_errors(service_result)
        return HTTPResponse[dtos.ShortenURLResponse](
            success=True,
            message="URL shortened successfully",
            data=dtos.ShortenURLResponse(
                id=short_url.id,
                original_url=short_url.original_url.value,
                short_code=short_url.short_code.value,
                expires_at=short_url.expires_at,
                created_at=short_url.created_at,
            ),
        )

    except AppBaseException:
        raise

    except DomainError as ex:
        raise BadRequestException(data=None, message=ex.message)

    except Exception as ex:
        logger.error(traceback.format_exc())
        raise ServerError(data=str(ex))


@router.get("/{short_code}", status_code=status.HTTP_302_FOUND)
async def visit_link(
    short_code: str,
    uow: T.Annotated[UOW, Depends(get_uow)],
) -> responses.RedirectResponse:
    try:
        cmd = commands.VisitLink(short_code)
        service_result = await commands.URLCommandHandler(uow).visit_link(cmd)

        original_url = handle_service_errors(service_result)

        return responses.RedirectResponse(
            url=original_url, status_code=status.HTTP_302_FOUND
        )

    except AppBaseException:
        raise

    except DomainError as ex:
        raise BadRequestException(data=None, message=ex.message)

    except Exception as ex:
        logger.error(traceback.format_exc())
        raise ServerError(data=str(ex))
