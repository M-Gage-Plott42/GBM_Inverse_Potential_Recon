"""Bounded FastAPI adapter for the deterministic calculation service."""

from __future__ import annotations

import json
import threading
from typing import Literal

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel, ConfigDict, Field, field_validator
from starlette.responses import JSONResponse
from starlette.types import ASGIApp, Message, Receive, Scope, Send

from .service import (
    ALGORITHM_VERSION,
    ALPHA_MAX,
    ALPHA_MIN,
    SCHEMA_VERSION,
    CalculationInputError,
    CalculationInvariantError,
    CalculationRequest,
    run_calculation,
)

HTTP_API_VERSION = "1.0"
SOURCE_STATUS = "unreleased"
MAX_REQUEST_BODY_BYTES = 1024

_CALCULATION_LOCK = threading.Lock()


async def _send_wire_error(send: Send, status_code: int, detail: str) -> None:
    body = json.dumps({"detail": detail}, separators=(",", ":")).encode("utf-8")
    await send(
        {
            "type": "http.response.start",
            "status": status_code,
            "headers": [
                (b"content-type", b"application/json"),
                (b"content-length", str(len(body)).encode("ascii")),
                (b"cache-control", b"no-store"),
                (b"x-content-type-options", b"nosniff"),
            ],
        }
    )
    await send({"type": "http.response.body", "body": body})


class BoundedHttpMiddleware:
    """Apply the local wire boundary before FastAPI parses a request body."""

    def __init__(self, app: ASGIApp, max_body_bytes: int) -> None:
        self.app = app
        self.max_body_bytes = max_body_bytes

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        async def hardened_send(message: Message) -> None:
            if message["type"] == "http.response.start":
                headers = [
                    header
                    for header in message.get("headers", [])
                    if header[0].lower()
                    not in {b"cache-control", b"x-content-type-options"}
                ]
                headers.extend(
                    [
                        (b"cache-control", b"no-store"),
                        (b"x-content-type-options", b"nosniff"),
                    ]
                )
                message["headers"] = headers
            await send(message)

        if scope.get("path") != "/v1/reconstruct" or scope.get("method") != "POST":
            await self.app(scope, receive, hardened_send)
            return

        headers = {key.lower(): value for key, value in scope.get("headers", [])}
        content_encoding = headers.get(b"content-encoding", b"identity").strip().lower()
        if content_encoding not in {b"", b"identity"}:
            await _send_wire_error(
                send, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, "unsupported media type"
            )
            return
        content_type = (
            headers.get(b"content-type", b"").split(b";", 1)[0].strip().lower()
        )
        if content_type != b"application/json":
            await _send_wire_error(
                send, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, "unsupported media type"
            )
            return
        content_length = headers.get(b"content-length")
        if content_length is not None:
            try:
                declared_length = int(content_length)
            except ValueError:
                await _send_wire_error(
                    send, status.HTTP_400_BAD_REQUEST, "invalid request"
                )
                return
            if declared_length < 0:
                await _send_wire_error(
                    send, status.HTTP_400_BAD_REQUEST, "invalid request"
                )
                return
            if declared_length > self.max_body_bytes:
                await _send_wire_error(
                    send,
                    status.HTTP_413_CONTENT_TOO_LARGE,
                    "request body too large",
                )
                return

        chunks: list[bytes] = []
        received_bytes = 0
        while True:
            message = await receive()
            if message["type"] == "http.disconnect":
                await _send_wire_error(
                    send, status.HTTP_400_BAD_REQUEST, "invalid request"
                )
                return
            if message["type"] != "http.request":
                continue
            chunk = message.get("body", b"")
            received_bytes += len(chunk)
            if received_bytes > self.max_body_bytes:
                await _send_wire_error(
                    send,
                    status.HTTP_413_CONTENT_TOO_LARGE,
                    "request body too large",
                )
                return
            chunks.append(chunk)
            if not message.get("more_body", False):
                break

        replayed = False

        async def replay_receive() -> Message:
            nonlocal replayed
            if replayed:
                return {"type": "http.request", "body": b"", "more_body": False}
            replayed = True
            return {
                "type": "http.request",
                "body": b"".join(chunks),
                "more_body": False,
            }

        await self.app(scope, replay_receive, hardened_send)


class _ClosedModel(BaseModel):
    """Reject fields outside the public wire contract."""

    model_config = ConfigDict(extra="forbid")


class ReconstructionRequest(_ClosedModel):
    """The only public calculation input."""

    alpha: float = Field(ge=ALPHA_MIN, le=ALPHA_MAX, allow_inf_nan=False)

    @field_validator("alpha", mode="before")
    @classmethod
    def require_json_number(cls, value: object) -> object:
        """Reject JSON booleans, strings, nulls, arrays, and objects."""

        if isinstance(value, bool) or not isinstance(value, (int, float)):
            # Pydantic converts ValueError, while TypeError escapes its validator.
            raise ValueError("alpha must be a JSON number")  # noqa: TRY004
        return value


class SoftwareIdentity(_ClosedModel):
    name: str


class CalculationIdentity(_ClosedModel):
    id: str
    algorithm_version: str
    software: SoftwareIdentity


class NormalizedInput(_ClosedModel):
    alpha: float


class UnitsContext(_ClosedModel):
    system: str
    hbar_squared_over_2m: float
    alpha: str
    potential: str


class WorkProfile(_ClosedModel):
    id: str
    r_min: float
    r_max: float
    r_points: int
    q_min: float
    q_max: float
    q_points: int
    grid_work: int


class CalculationMetrics(_ClosedModel):
    density_l2_rel: float
    density_max_rel_window: float
    density_norm_trapz: float
    potential_l2_rel_window: float
    potential_max_abs_window: float


class ReconstructionResponse(_ClosedModel):
    schema_version: str
    calculation: CalculationIdentity
    input: NormalizedInput
    units: UnitsContext
    profile: WorkProfile
    metrics: CalculationMetrics
    quality_gate: str
    limitations: list[str]


class HealthResponse(_ClosedModel):
    status: Literal["live", "ready"]


class VersionResponse(_ClosedModel):
    api_version: str
    schema_version: str
    algorithm_version: str
    source_status: Literal["unreleased"]


class ErrorResponse(_ClosedModel):
    detail: str


app = FastAPI(
    title="GBM Inverse Potential Reconstruction API",
    summary="Bounded deterministic harmonic-oscillator reconstruction",
    version=HTTP_API_VERSION,
    docs_url="/docs",
    redoc_url=None,
    openapi_url="/openapi.json",
    swagger_ui_oauth2_redirect_url=None,
)
app.add_middleware(BoundedHttpMiddleware, max_body_bytes=MAX_REQUEST_BODY_BYTES)


@app.exception_handler(RequestValidationError)
async def invalid_request(
    _request: Request, _exception: RequestValidationError
) -> JSONResponse:
    """Return a finite generic error even when a parser accepts NaN tokens."""

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        content={"detail": "invalid request"},
    )


@app.exception_handler(Exception)
async def internal_error(_request: Request, _exception: Exception) -> JSONResponse:
    """Keep unexpected implementation details out of HTTP responses."""

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "internal server error"},
    )


@app.get("/health/live", response_model=HealthResponse, tags=["operations"])
def health_live() -> HealthResponse:
    """Report that the HTTP process is running."""

    return HealthResponse(status="live")


@app.get(
    "/health/ready",
    response_model=HealthResponse,
    tags=["operations"],
)
def health_ready() -> HealthResponse:
    """Report readiness; the adapter has no external startup dependency."""

    return HealthResponse(status="ready")


@app.get("/version", response_model=VersionResponse, tags=["operations"])
def version() -> VersionResponse:
    """Return contract identities without implying a package release."""

    return VersionResponse(
        api_version=HTTP_API_VERSION,
        schema_version=SCHEMA_VERSION,
        algorithm_version=ALGORITHM_VERSION,
        source_status=SOURCE_STATUS,
    )


@app.post(
    "/v1/reconstruct",
    response_model=ReconstructionResponse,
    responses={
        status.HTTP_400_BAD_REQUEST: {"model": ErrorResponse},
        status.HTTP_413_CONTENT_TOO_LARGE: {"model": ErrorResponse},
        status.HTTP_415_UNSUPPORTED_MEDIA_TYPE: {"model": ErrorResponse},
        status.HTTP_422_UNPROCESSABLE_CONTENT: {"model": ErrorResponse},
        status.HTTP_429_TOO_MANY_REQUESTS: {"model": ErrorResponse},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorResponse},
        status.HTTP_503_SERVICE_UNAVAILABLE: {"model": ErrorResponse},
    },
    tags=["calculation"],
)
def reconstruct(
    request: ReconstructionRequest, wire_request: Request
) -> ReconstructionResponse:
    """Run one fixed-profile reconstruction without storing the input."""

    if wire_request.query_params:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="invalid request",
        )
    if not _CALCULATION_LOCK.acquire(blocking=False):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="calculation capacity is busy",
            headers={"Retry-After": "1"},
        )
    try:
        result = run_calculation(CalculationRequest(alpha=request.alpha))
    except CalculationInputError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="invalid calculation request",
        ) from exc
    except CalculationInvariantError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="calculation unavailable",
        ) from exc
    finally:
        _CALCULATION_LOCK.release()
    return ReconstructionResponse.model_validate(result.to_dict())
