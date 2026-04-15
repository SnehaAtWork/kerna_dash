from fastapi import Request
from fastapi.responses import JSONResponse

from app.shared.exceptions import NotFoundError, ValidationError


def register_exception_handlers(app):

    @app.exception_handler(NotFoundError)
    async def not_found_handler(request: Request, exc: NotFoundError):
        return JSONResponse(
            status_code=404,
            content={"detail": str(exc)}
        )

    @app.exception_handler(ValidationError)
    async def validation_handler(request: Request, exc: ValidationError):
        return JSONResponse(
            status_code=422,
            content={"detail": str(exc)}
        )