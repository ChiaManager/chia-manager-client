import logging
from inspect import getsourcefile
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path

from node.NodeConfig import NodeConfig

class NodeLogger:
    def __init__(self, log_level: int = logging.INFO):
        self.node_cconfig = NodeConfig()

        self.log_dir = Path(getsourcefile(lambda:0)).absolute().parents[1].joinpath('log')
        self.log_level = self.node_cconfig['Logging'].get('log_level') or log_level

        self.log_backup_count = self.node_cconfig['Logging']['log_level'] or 3
        self.log_to_stdout = self.node_cconfig['Logging']['log_to_stdout'] or False

        self.__setup_logger()

    def __setup_logger(self):
        logger = logging.getLogger()
        logger.setLevel(self.log_level)
        log_format = "%(asctime)s [%(levelname)-5.5s] [%(filename)s:%(lineno)s] [%(funcName)s()] %(message)s"
        log_formatter = logging.Formatter(log_format)
        
        # create log dir if not exist
        if not self.log_dir.exists():
            self.log_dir.mkdir(parents=True)

        # add handler to log into stdout
        if self.log_to_stdout:
            print(f"Log to stdout is active.")
            stream_handler = logging.StreamHandler()
            stream_handler.setFormatter(log_formatter)
            stream_handler.setLevel(self.log_level)
            logger.addHandler(stream_handler)

        # add default log with file rotation
        file_handler = TimedRotatingFileHandler(
            filename=self.log_dir.joinpath('node.log'), when='midnight', backupCount=self.log_backup_count)
        file_handler.setFormatter(log_formatter)
        file_handler.setLevel(self.log_level)
        logger.addHandler(file_handler)

        # add error log
        error_file_handler = TimedRotatingFileHandler(
            filename=self.log_dir.joinpath('node_error.log'), when='midnight', backupCount=self.log_backup_count)
        error_file_handler.setFormatter(log_formatter)
        error_file_handler.setLevel(logging.ERROR)
        logger.addHandler(error_file_handler)
