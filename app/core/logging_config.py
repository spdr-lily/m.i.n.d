import logging
import sys
from app.core.config import settings


def setup_logging():
    log_level = logging.DEBUG if settings.debug else logging.INFO

    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(log_level)
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    handler.setFormatter(formatter)
    root_logger.addHandler(handler)

    for name in ("uvicorn", "uvicorn.access", "sqlalchemy.engine"):
        logging.getLogger(name).setLevel(logging.WARNING)

    logging.getLogger("mind").setLevel(log_level)

    return logging.getLogger("mind")
