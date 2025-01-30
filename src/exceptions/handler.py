from fastapi.requests import Request
from fastapi.responses import JSONResponse

from src.exceptions.base_exception import BaseHTTPException
from src.main.logging import get_logger


class ExceptionHandler:
    logger = get_logger(__name__)

    async def __call__(self, request: Request, exc: BaseHTTPException) -> JSONResponse:
        self.logger.error(
            f"Exception occurred while processing {request.url}: {exc.exception}, "
            + "Trace:"
            + exc.trace
        )

        return JSONResponse(
            status_code=exc.status_code,
            content={"message": getattr(exc, "message", str(exc))},
            headers=exc.headers,
        )
