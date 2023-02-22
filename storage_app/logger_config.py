from loguru import logger

logger.add(
    "logging_records/debug.json",
    format="{time}{level}{message}",
    level="INFO",
    rotation="11:00",
    compression="zip",
    serialize=True
)
