# looger.py
import os
import logging
from logging.handlers import RotatingFileHandler


def setup_logging(log_dir="logs", log_name="translator.log"):
    """初始化日志系统"""
    os.makedirs(log_dir, exist_ok=True)

    log_path = os.path.join(log_dir, log_name)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            RotatingFileHandler(log_path, maxBytes=1 * 1024 * 1024, backupCount=5),
            logging.StreamHandler()
        ]
    )

    return logging.getLogger("GameTranslator")


logger = setup_logging()
