import asyncio
import logging
import time

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.api import approvals, auth, dashboard, health, requests as requests_api
from app.config import settings
from app.utils.metrics import http_request_duration_seconds, http_requests_total
from app.workers.notification_worker import run_worker

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    worker_task = asyncio.create_task(run_worker())
    logger.info("app_started name=%s version=%s", settings.APP_NAME, settings.APP_VERSION)
    try:
        yield
    finally:
        worker_task.cancel()
        try:
            await worker_task
        except asyncio.CancelledError:
            pass
        logger.info("app_stopped")


app = FastAPI(
    title="ServiceOps Portal",
    version=settings.APP_VERSION,
    lifespan=lifespan,
)


@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    duration = time.perf_counter() - start
    endpoint = request.scope.get("route").path if request.scope.get("route") else request.url.path
    http_requests_total.labels(
        method=request.method, endpoint=endpoint, status=response.status_code
    ).inc()
    http_request_duration_seconds.labels(
        method=request.method, endpoint=endpoint
    ).observe(duration)
    return response


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.exception("unhandled_exception path=%s", request.url.path)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )


app.include_router(health.router)
app.include_router(auth.router)
app.include_router(requests_api.router)
app.include_router(approvals.router)
app.include_router(dashboard.router)
