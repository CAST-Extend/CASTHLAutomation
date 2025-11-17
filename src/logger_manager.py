import logging
import os
from datetime import datetime

class LoggerManager:
    """
    Reusable Logger Manager class.
    Creates independent log files for each process/method.
    """

    @staticmethod
    def get_logger(name, log_dir="logs", log_level=logging.INFO):
        """
        Returns a logger that logs to both file and console.

        Args:
            name (str): Logger name (e.g., 'find_new_applications')
            log_dir (str): Directory to store the log file
            log_level (int): Logging level (default: INFO)
        """
        # Ensure directory exists
        os.makedirs(log_dir, exist_ok=True)

        # Log file name: <log_dir>/<name>_<timestamp>.log
        log_filename = os.path.join(
            log_dir,
            f"{name}_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.log"
        )

        # Create logger
        logger = logging.getLogger(name)
        logger.setLevel(log_level)

        # Prevent duplicate handlers
        if logger.hasHandlers():
            logger.handlers.clear()

        # File handler
        file_handler = logging.FileHandler(log_filename, mode='a', encoding='utf-8')
        file_handler.setLevel(log_level)

        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level)

        # Formatter
        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        # Attach handlers
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

        return logger
