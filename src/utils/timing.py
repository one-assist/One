import logging
import time 
from contextlib import contextmanager

logger = logging.getLogger(__name__)

@contextmanager
def measure(operation: str):
    started = time.perf_counter()

    try:
        yield
    finally:
        elapsed = time.perf_counter() - started
        logger.debug("%s took %.3fs", operation, elapsed)