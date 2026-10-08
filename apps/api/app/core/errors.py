from fastapi import Request, status
from fastapi.responses import JSONResponse
from app.core.logging import logger


class CertiGuardException(Exception):
    def __init__(self, message: str, code: str = "INTERNAL_ERROR", status_code: int = 500):
        self.message = message
        self.code = code
        self.status_code = status_code
        super().__init__(message)


async def certiguard_exception_handler(request: Request, exc: CertiGuardException):
    logger.error(f"CertiGuard Error [{exc.code}]: {exc.message} (Path: {request.url.path})")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.code,
                "message": exc.message,
                "path": str(request.url.path)
            }
        }
    )


async def generic_exception_handler(request: Request, exc: Exception):
    logger.exception(f"Unhandled Internal Server Error: {str(exc)} (Path: {request.url.path})")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected internal error occurred. Please try again later.",
                "path": str(request.url.path)
            }
        }
    )
