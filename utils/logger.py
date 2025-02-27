"""Logging configuration"""
import logging
import sys
from logging.handlers import RotatingFileHandler

def setup_logger(name: str, log_file: str = 'app.log', log_level: str = 'INFO') -> logging.Logger:
    """Configure and return a logger instance"""
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, log_level))

    # File handler with rotation
    file_handler = RotatingFileHandler(
        log_file, maxBytes=1024*1024, backupCount=5
    )
    file_handler.setFormatter(
        logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    )

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(
        logging.Formatter('%(levelname)s - %(message)s')
    )

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger
