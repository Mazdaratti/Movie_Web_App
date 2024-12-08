"""
This module provides a centralized logging configuration for the application.

The logger is configured to use a rotating file handler, ensuring that log files
do not grow indefinitely. It includes a timestamp in log messages for better
tracking and debugging. The logger is reusable across all application modules.

Features:
    - Rotating file handler to limit log file size and maintain backups.
    - Timestamped log messages for better tracking.
    - Single reusable logger instance for consistency.

Exports:
    logger: A pre-configured logger instance ready for use in other modules.
"""

import logging
from logging.handlers import RotatingFileHandler


def configure_logger():
    """
    Configures and returns a logger with a rotating file handler and timestamped format.

    Returns:
        logging.Logger: Configured logger instance.
    """
    logger = logging.getLogger("app_logger")  # Custom logger name to avoid conflicts
    logger.setLevel(logging.ERROR)  # Set the global log level

    # Create a rotating file handler
    handler = RotatingFileHandler('app.log', maxBytes=10000, backupCount=1)
    handler.setLevel(logging.ERROR)

    # Set a formatter with a timestamp
    formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S'
    )
    handler.setFormatter(formatter)

    # Add the handler to the logger
    if not logger.handlers:  # Avoid duplicate handlers
        logger.addHandler(handler)

    return logger


# Export the logger for use in other modules
logger = configure_logger()
