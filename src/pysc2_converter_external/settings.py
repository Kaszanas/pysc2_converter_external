import enum
import logging
import os

from dotenv import load_dotenv

load_dotenv()


LOG_LEVEL = os.getenv("LOG_LEVEL", "")


LOGGING_FORMAT = "[%(asctime)s] %(levelname)s: %(message)s"


class LogLevel(str, enum.Enum):
    """Log levels for the application."""

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


def initialize_logging(log_level: LogLevel):
    """Initialize logging with the specified log level."""

    if LOG_LEVEL:
        print(
            f"Overriding log level with value from environment variable LOG_LEVEL: {LOG_LEVEL}"
        )
        log_level = LOG_LEVEL

    numeric_level = getattr(logging, log_level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError(f"Invalid log level: {numeric_level}")
    logging.basicConfig(level=numeric_level, format=LOGGING_FORMAT, force=True)

    logging.info(f"Logging initialized with level: {log_level}!")
