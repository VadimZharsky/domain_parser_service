import logging
import os
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler


class FileLogger:
    def __init__(self, logger_name: str, logger_lvl: int = logging.ERROR) -> None:
        FileLogger.check_path(logger_name)
        self.format = "%(asctime)s - %(levelname)s - %(message)s"
        self.file_name = f"logs/{logger_name}/{logger_name}.log"
        self.logger_name = logger_name
        self._logger = logging.getLogger(logger_name)
        self._logger.setLevel(logger_lvl)
        self._logger.addHandler(self._set_timed_handler())

    @property
    def get_logger(self) -> logging.Logger:
        return self._logger

    def _set_timed_handler(self) -> TimedRotatingFileHandler:
        handler = TimedRotatingFileHandler(
            filename=self.file_name,
            when="midnight",
            backupCount=30,
            interval=1,
        )
        handler.setFormatter(logging.Formatter(self.format))
        return handler

    def _set_rotating_file_handler(self) -> RotatingFileHandler:
        handler = RotatingFileHandler(
            filename=self.file_name,
            maxBytes=100 * 1000000,
            backupCount=1,
            encoding="utf-8",
        )
        handler.setFormatter(logging.Formatter(self.format))
        return handler

    @staticmethod
    def check_path(logger_folder: str) -> None:
        if not os.path.exists(f"logs/{logger_folder}"):
            os.makedirs(f"logs/{logger_folder}")
