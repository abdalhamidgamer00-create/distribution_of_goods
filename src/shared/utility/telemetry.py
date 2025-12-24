"""Performance telemetry utility for tracking and logging execution time."""

import time
from contextlib import contextmanager
from src.shared.utility.logging_utils import get_logger

logger = get_logger(__name__)


@contextmanager
def execution_timer(service_name: str):
    """Context manager to measure and log the execution time of a block."""
    start_time = time.perf_counter()
    try:
        yield
    finally:
        end_time = time.perf_counter()
        duration = end_time - start_time
        logger.info(
            f"Service '{service_name}' execution took {duration:.4f} seconds."
        )


class TelemetryTracker:
    """Helper to record and retrieve timing metrics."""
    def __init__(self):
        self._metrics = {}

    def record_duration(self, name: str, duration: float):
        """Stores the duration of a specific operation."""
        self._metrics[name] = duration

    def get_metrics(self) -> dict:
        """Returns all recorded metrics."""
        return self._metrics
