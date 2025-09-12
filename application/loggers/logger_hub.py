import logging

from application.constants import AppConstants
from application.loggers.file_logger import FileLogger


class LoggerHub:
    _RELEASE = f"RELEASE FROM: {AppConstants.RELEASE_DATA}"
    _TITLE = f"TITLE: {AppConstants.APP_TITLE}"
    _VERSION = f"VERSION: {AppConstants.VERSION}"
    _BOUND1: str = ">" * len(_RELEASE)
    _BOUND2: str = "<" * len(_RELEASE)

    def __init__(self) -> None:
        self.service_log = FileLogger(
            logger_name=AppConstants.LOGGER_NAME, logger_lvl=logging.INFO
        ).get_logger
        self.api_log = FileLogger(logger_name="api", logger_lvl=logging.INFO).get_logger

    def initialize(self) -> None:
        LoggerHub.log_startup(self.service_log)
        LoggerHub.log_startup(self.api_log)

    @staticmethod
    def log_startup(logger: logging.Logger) -> None:
        logger.info(LoggerHub._BOUND1)
        logger.info(LoggerHub._TITLE)
        logger.info(LoggerHub._VERSION)
        logger.info(LoggerHub._RELEASE)
        logger.info(LoggerHub._BOUND2)
