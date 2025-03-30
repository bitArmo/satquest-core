import logging
import os
import sys
from logging.handlers import RotatingFileHandler

def get_log_path():
    # Check if we're running tests
    if 'pytest' in sys.modules:
        log_dir = 'tests/logs'
    else:
        log_dir = 'logs'
    
    # Create logs directory if it doesn't exist
    os.makedirs(log_dir, exist_ok=True)
    return os.path.join(log_dir, 'app.log')

# Configure logging
def setup_logging():
    # Create a logger
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # Create formatters
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # Create and configure file handler
    log_path = get_log_path()
    file_handler = RotatingFileHandler(
        log_path,
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)

    # Create and configure console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)

    # Remove any existing handlers
    logger.handlers.clear()

    # Add handlers to logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger 