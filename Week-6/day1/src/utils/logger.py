import logging
import os
from datetime import datetime


def setup_logger(name, log_dir='logs', level=logging.INFO):
    os.makedirs(log_dir, exist_ok=True)

    logger = logging.getLogger(name)
    logger.setLevel(level)

    if logger.hasHandlers():
        logger.handlers.clear()

    log_file = os.path.join(
        log_dir,
        f'{name}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'
    )

    file_handler = logging.FileHandler(log_file)
    console_handler = logging.StreamHandler()

    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger