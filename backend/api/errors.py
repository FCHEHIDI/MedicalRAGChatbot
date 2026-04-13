"""
Centralized HTTP exception mapping and request correlation.

Order of registration: validation → domain → HTTP → fallback.
"""

from __future__ import annotations

import logging
import uuid
from typing import Any

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from exceptions.domain import RAGDomainError
from resilience.context import request_id_ctx

logger = logging.getLogger("medical_rag.api")

REQUEST_ID_HEADER = "X-Request-ID"


def _request_id(request: Request) -> str | None:
    return getattr(request.state, "request_id", None)


class RequestIDMiddleware(BaseHTTPMiddleware):
    """Propagate or generate X-Request-ID on every request/response."""

    async def dispatch(self, request: Request, call_next: Any) -> Any:
        incoming = request.headers.get(REQUEST_ID_HEADER)
        rid = incoming or str(uuid.uuid4())
        request.state.request_id = rid
        token = request_id_ctx.set(rid)
        try:
            response = await call_next(request)
            response.headers[REQUEST_ID_HEADER] = rid
            return response
        finally:
            request_id_ctx.reset(token)


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request,
        exc: RequestValidationError,
    ) -> JSONResponse:
        rid = _request_id(request)
        logger.warning(
            "validation_error request_id=%s errors=%s",
            rid,
            exc.errors(),
        )
        return JSONResponse(
            status_code=422,
            content={
                "detail": exc.errors(),
                "code": "validation_error",
                "request_id": rid,
            },
        )

    @app.exception_handler(RAGDomainError)
    async def rag_domain_exception_handler(
        request: Request,
        exc: RAGDomainError,
    ) -> JSONResponse:
        rid = _request_id(request)
        logger.error(
            "rag_domain_error request_id=%s code=%s message=%s",
            rid,
            exc.code,
            exc.message,
        )
        return JSONResponse(
            status_code=500,
            content={
                "detail": exc.message,
                "code": exc.code,
                "request_id": rid,
            },
        )

    @app.exception_handler(HTTPException)
    async def http_exception_handler(
        request: Request,
        exc: HTTPException,
    ) -> JSONResponse:
        rid = _request_id(request)
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "detail": exc.detail,
                "request_id": rid,
            },
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(
        request: Request,
        exc: Exception,
    ) -> JSONResponse:
        rid = _request_id(request)
        logger.exception("unhandled_error request_id=%s", rid)
        return JSONResponse(
            status_code=500,
            content={
                "detail": "Internal server error",
                "code": "internal_error",
                "request_id": rid,
            },
        )
