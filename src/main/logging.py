import logging

from src.main.settings import settings


class LoggingFormatter(logging.Formatter):
    info_frmt = "\x1b[38;20m"
    warning_frmt = "\x1b[33;20m"
    error_frmt = "\x1b[31;20m"
    debug_frmt = "\x1b[1;20m"
    critical_frmt = "\x1b[1;41m"
    reset = "\x1b[0m"
    format_str: str = (
        "%(asctime)s - %(levelname)s: " "%(message)s (%(filename)s:%(lineno)d)"
    )

    FORMATS = {
        logging.DEBUG: debug_frmt + format_str + reset,
        logging.INFO: info_frmt + format_str + reset,
        logging.WARNING: warning_frmt + format_str + reset,
        logging.ERROR: error_frmt + format_str + reset,
    }

    def format(self, record: logging.LogRecord) -> str:
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


LOG_LEVEL = settings.LOGGING_LEVEL.to_logging_type()
STREAM_HANDLER = logging.StreamHandler()
STREAM_HANDLER.setLevel(LOG_LEVEL)
STREAM_HANDLER.setFormatter(LoggingFormatter())

# unicorn logging handling
L = logging.getLogger("uvicorn")
L.handlers.clear()
L.addHandler(STREAM_HANDLER)

# fastapi logging handling
L = logging.getLogger("uvicorn.access")
L.handlers.clear()
L.addHandler(STREAM_HANDLER)


def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(LOG_LEVEL)
    logger.addHandler(STREAM_HANDLER)
    logger.propagate = False

    return logger
