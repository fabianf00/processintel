import logging
import logging.config
from os import getenv

LOG_LEVEL = getenv("PROCESSINTEL_LOG_LEVEL", "warn").upper()

logging_config = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "simple": {"format": "[%(asctime)s] %(name)s - %(levelname)s : %(message)s"}
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": LOG_LEVEL,
            "formatter": "simple",
            "stream": "ext://sys.stdout",
        }
    },
    "loggers": {"": {"level": LOG_LEVEL, "handlers": ["console"]}},
}

logging.config.dictConfig(logging_config)


def get_logger(name):
    return logging.getLogger(name)
