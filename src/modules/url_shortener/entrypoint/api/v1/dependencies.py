from fastapi import Request

from .exceptions import BadRequestException
from ....infrastructure.code_generator import CodeGenerator


from ....infrastructure import UOW


async def get_uow() -> UOW:
    return UOW()


async def get_code_generator() -> CodeGenerator:
    return CodeGenerator()


async def get_client_ip(
    request: Request,
    trust_proxy: bool = True,  # Set False if not behind proxy
) -> str:
    """
    Extract real client IP considering proxies and load balancers.

    Header priority:
    1. X-Forwarded-For (standard)
    2. X-Real-IP (nginx)
    3. CF-Connecting-IP (Cloudflare)
    4. True-Client-IP (Akamai)
    5. request.client.host (direct)
    """
    if trust_proxy:
        proxy_headers = [
            "X-Forwarded-For",  # Standard
            "X-Real-IP",  # Nginx
            "CF-Connecting-IP",  # Cloudflare
            "True-Client-IP",  # Akamai
            "X-Cluster-Client-IP",  # Custom
        ]

        for header in proxy_headers:
            ip = request.headers.get(header)
            if ip:
                if header == "X-Forwarded-For":
                    ip = ip.split(",")[0].strip()
                return ip

    if request.client and request.client.host:
        return request.client.host

    raise BadRequestException(message="Cannot determine client IP")
