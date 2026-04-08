"""Logging helpers for service startup."""

import logging
import sys

from pythonjsonlogger.json import JsonFormatter


def configure_logging() -> None:
    """Configure JSON-formatted root logging for local and container runs."""

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(
        JsonFormatter("%(asctime)s %(levelname)s %(name)s %(message)s")
    )

    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(handler)
