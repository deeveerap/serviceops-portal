import asyncio
import logging
import signal
from contextlib import contextmanager

from app.database import SessionLocal
from app.services import notification_service

logger = logging.getLogger(__name__)

POLL_INTERVAL_SECONDS = 30


def _process_batch() -> int:
    processed = 0
    with SessionLocal() as db:
        try:
            pending = notification_service.get_pending(db)
            for note in pending:
                notification_service.mark_sent(db, note)
                processed += 1
        except Exception:
            logger.exception("notification_batch_failed")
            db.rollback()
    return processed


async def run_worker() -> None:
    logger.info("notification_worker_started interval=%ss", POLL_INTERVAL_SECONDS)
    stop = asyncio.Event()

    def _handle_signal(*_):
        logger.info("notification_worker_stopping")
        stop.set()

    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, _handle_signal)

    while not stop.is_set():
        processed = await asyncio.to_thread(_process_batch)
        if processed:
            logger.info("notification_batch_processed count=%s", processed)
        try:
            await asyncio.wait_for(stop.wait(), timeout=POLL_INTERVAL_SECONDS)
        except asyncio.TimeoutError:
            continue

    logger.info("notification_worker_stopped")


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )
    asyncio.run(run_worker())
