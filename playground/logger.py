import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler


class ColoredFormatter(logging.Formatter):
    """Custom formatter to add colors to log messages based on their level."""

    COLORS = {
        logging.DEBUG: "\033[94m",  # Blue
        logging.INFO: "\033[92m",   # Green
        logging.WARNING: "\033[93m",  # Yellow
        logging.ERROR: "\033[91m",   # Red
        logging.CRITICAL: "\033[95m"  # Magenta
    }
    RESET = "\033[0m"

    def format(self, record):
        color = self.COLORS.get(record.levelno, self.RESET)
        message = super().format(record)
        return f"{color}{message}{self.RESET}"

def setup_logging(app_name, level=logging.DEBUG, module_levels=None):
    """Configure root logging and optional per-module log levels.

    Args:
        app_name (str): Base name for the log file (<app_name>.log).
        level (int): Default/root log level.
        module_levels (dict): Optional logger level overrides, e.g.
            {"orchestrator": logging.DEBUG, "zmq_pub_sub": logging.INFO}
    """
    if module_levels is None:
        module_levels = {}

    log_format = logging.Formatter(
        "{levelname: <8}:{asctime}:{name:<18}({lineno}): {message}",
        datefmt="%Y-%m-%d %H:%M:%S",
        style="{",
    )
    
    root_logger = logging.getLogger()
    if root_logger.hasHandlers():
        return
    root_logger.setLevel(level)
    
    console_handler = logging.StreamHandler(sys.stdout)
    formatter = ColoredFormatter(
        "{levelname: <8}:{asctime}:{name:<18}({lineno}): {message}",
        datefmt="%Y-%m-%d %H:%M:%S",
        style="{",
    )
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    log_file_path = Path(f"{app_name}.log")
    file_handler = RotatingFileHandler(str(log_file_path), maxBytes=5*1024*1024, backupCount=5)
    file_handler.setFormatter(log_format)
    root_logger.addHandler(file_handler)

    for logger_name, logger_level in module_levels.items():
        logging.getLogger(logger_name).setLevel(logger_level)

    logging.info(
        "Logging initialized for {} at level {} - Writing to {}".format(
            app_name, logging.getLevelName(level), log_file_path.absolute()
        )
    )