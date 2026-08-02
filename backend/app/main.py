from __future__ import annotations

import time
import uuid

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response

from app.api.routes import router
from app.core.config import settings
from app.metrics.prometheus import METRICS
from app.scoring.service import ACTIVE_MODEL

app = FastAPI(title="Sentinel API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(router)


@app.middleware("http")
async def trace_requests(request: Request, call_next):
    trace_id = request.headers.get("x-trace-id", str(uuid.uuid4()))
    request.state.trace_id = trace_id
    started = time.perf_counter()
    response = await call_next(request)
    elapsed_ms = (time.perf_counter() - started) * 1000
    METRICS.observe(request.url.path, response.status_code, elapsed_ms)
    response.headers["x-trace-id"] = trace_id
    response.headers["x-content-type-options"] = "nosniff"
    response.headers["x-frame-options"] = "DENY"
    response.headers["referrer-policy"] = "no-referrer"
    response.headers["content-security-policy"] = "default-src 'none'; frame-ancestors 'none'"
    if settings.production:
        response.headers["strict-transport-security"] = "max-age=31536000; includeSubDomains"
    return response


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    return JSONResponse(
        status_code=422,
        content={
            "trace_id": getattr(request.state, "trace_id", str(uuid.uuid4())),
            "error": "validation_error",
            "details": exc.errors(),
        },
    )


@app.get("/healthz")
def healthz() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/readyz", response_model=None)
def readyz() -> Response | dict[str, str]:
    if settings.production and not ACTIVE_MODEL.using_bundle:
        return JSONResponse(
            status_code=503, content={"status": "not_ready", "reason": "model bundle unavailable"}
        )
    return {"status": "ready", "model": ACTIVE_MODEL.model_name}
