# logger.py
import os
import logging
from logging.handlers import RotatingFileHandler


def setup_logging(
        name="GameTranslator",
        log_dir="logs",
        log_name="translator.log",
        level=logging.INFO,
        max_bytes=1 * 1024 * 1024,
        backup_count=5,
        console=True
):
    """
    初始化日志系统
    - name: 日志记录器名称
    - log_dir: 日志文件夹
    - log_name: 日志文件名
    - level: 日志等级
    - max_bytes: 日志文件最大大小
    - backup_count: 日志轮转数量
    - console: 是否输出到控制台
    """
    os.makedirs(log_dir, exist_ok=True)
    log_path = os.path.join(log_dir, log_name)

    # 创建 Logger
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # 防止重复添加 Handler
    if not logger.handlers:
        # 文件 Handler（带轮转）
        file_handler = RotatingFileHandler(log_path, maxBytes=max_bytes, backupCount=backup_count)
        file_formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

        # 控制台 Handler
        if console:
            console_handler = logging.StreamHandler()
            console_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
            console_handler.setFormatter(console_formatter)
            logger.addHandler(console_handler)

    # 屏蔽第三方库信息（可选）
    logging.getLogger("paddle").setLevel(logging.WARNING)
    logging.getLogger("PaddleOCR").setLevel(logging.WARNING)
    logging.getLogger("onednn_context").setLevel(logging.WARNING)

    return logger


# -------------------------
# 全局 logger
# -------------------------
logger = setup_logging(level=logging.DEBUG)  # DEBUG 级别及以上都会输出
