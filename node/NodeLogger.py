
import sys
import logging
import datetime
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path

from node.NodeConfig import NodeConfig

class NodeLogger:
    def __init__(self, log_level: int = logging.INFO, log_to_stdout: bool = False):
        self.log_config = NodeConfig().logging
        
        self.log_dir = Path(self.log_config.get('' ,__file__)).absolute().parents[1].joinpath('log')
        self.log_level = self.log_config.get('log_level', log_level)
        self.log_backup_count = self.log_config.get('log_backup_count', 3)
        self.log_to_stdout = self.log_config.get('log_to_stdout', log_to_stdout)
        
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
        
