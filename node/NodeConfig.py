import sys
import os
import logging
from pathlib import Path
from configparser import RawConfigParser

from node import __version__
from node.Singleton import Singleton

log = logging.getLogger()


class NodeConfig(RawConfigParser):
    _instances = {}

    def __init__(self):
        super().__init__()
        root_path = Path(os.path.realpath(__file__)).parent
        self.config_dir = Path(root_path).parent.joinpath('config')
        self.chia_config_file = self.config_dir.joinpath('node.ini')

        self.__server = None
        self.__port = None
        self.__socket_dir = None
        self.auth_hash = None
        self.logging = {}
        self._check_log_and_config_path()

        self.load_config()
 
    @classmethod
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(NodeConfig, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

    def load_config(self):              
        log.debug(f"self.chia_config_file: {self.chia_config_file}")

        self.read(self.chia_config_file)
        connection_info = self['Connection']

        self.__server = format(connection_info["server"])
        self.__port = format(connection_info["port"])
        self.__socket_dir = format(connection_info["socketdir"])
        
        if self.has_option('Node', 'authhash'):
            self.auth_hash = format(self["Node"]["authhash"])
        
        # log config
        self.logging = self['Logging']

    def get_script_info(self):
        return __version__

    def get_connection(self):
        return f"wss://{self.__server}:{self.__port}{self.__socket_dir}"

    def get_chia_path(self):
        return self["Chia"]["chia_blockchain_path"]

    def update_config(self, section, key, value):
        log.debug("Write new config..")
        self[section][key] = value
        with open(self.chia_config_file, "w") as conf:
            print(conf)
            self.write(conf)

        log.debug("Write new config.. Done!")
        log.debug("Reload config..")
        self.read(self.chia_config_file)
        log.debug("Reload config.. Done!")

    def _check_log_and_config_path(self):

        if not self.config_dir.exists():
            log.info(f"Config folder does not exists. Create: {self.config_dir}")
            os.makedirs(self.config_dir)

        if not self.chia_config_file.exists():
            log.info("Config file does not exists!")
            log.info("Please configure your settings in node/node.ini \n" \
                     "The sample file can be found at: node/example.node.ini\n" \
                     "Exiting..")
            sys.exit(0)
