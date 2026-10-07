from fastapi import APIRouter, Response
from sqlalchemy import text

from app.database import engine
from app.utils.metrics import metrics_response

router = APIRouter(tags=["health"])


@router.get("/health")
def health():
    return {"status": "ok"}


@router.get("/ready")
def ready():
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return {"status": "ready"}
    except Exception as exc:
        return Response(
            content=f'{{"status":"not_ready","error":"{exc}"}}',
            media_type="application/json",
            status_code=503,
        )


@router.get("/metrics")
def metrics():
    data, content_type = metrics_response()
    return Response(content=data, media_type=content_type)
