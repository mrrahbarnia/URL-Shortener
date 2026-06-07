from fastapi import APIRouter

from src.core.config import ENVS

router = APIRouter(prefix=f"{ENVS.FASTAPI.ENDPOINT_PREFIX}")

# router.include_router(router=health_check_router)