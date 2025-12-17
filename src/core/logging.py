import logging
import os
from logging.handlers import RotatingFileHandler


def setup_logging(level: str = "INFO", log_dir: str = "data/logs", filename: str = "app.log") -> None:
    os.makedirs(log_dir, exist_ok=True)
    log_path = os.path.join(log_dir, filename)

    fmt = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    datefmt = "%Y-%m-%d %H:%M:%S"

    root = logging.getLogger()  # type: ignore[attr-defined]
    root.setLevel(level.upper())

    ch = logging.StreamHandler()  # type: ignore[attr-defined]
    ch.setFormatter(logging.Formatter(fmt=fmt, datefmt=datefmt))  # type: ignore[attr-defined]
    root.addHandler(ch)

    fh = RotatingFileHandler(log_path, maxBytes=2_000_000, backupCount=3, encoding="utf-8")
    fh.setFormatter(logging.Formatter(fmt=fmt, datefmt=datefmt))  # type: ignore[attr-defined]
    root.addHandler(fh)
