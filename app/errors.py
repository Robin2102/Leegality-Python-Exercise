
"""Make every error response look like the spec: {"error": "..."}."""
from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

def _describe(error: dict) -> str:
    if error["type"] == "json_invalid":
        return "Request body is not valid JSON"
    field = ".".join(str(part) for part in error["loc"][1:]) or "request"
    return f"{field}: {error['msg']}"

def register_error_handlers(app: FastAPI):
    @app.exception_handler(StarletteHTTPException)
    async def http_error(_request: Request, exc: HTTPException) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": exc.detail},
        )

    @app.exception_handler(RequestValidationError)
    async def validation_error(_request: Request, exc: RequestValidationError) -> JSONResponse:
        message = "; ".join(_describe(e) for e in exc.errors())
        return JSONResponse(status_code=400, content={"error": message})

    @app.exception_handler(Exception)
    async def unexpected_error(_request: Request, _exc: Exception) -> JSONResponse:
        # Starlette still re-raises after this, so the traceback is logged.
        return JSONResponse(status_code=500, content={"error": "Internal server error"})