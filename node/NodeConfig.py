import sys
import os
import logging
from pathlib import Path
from configparser import RawConfigParser

from node import version
from node.Singleton import Singleton

log = logging.getLogger()


class NodeConfig(RawConfigParser):
    _instances = {}

    def __init__(self):
        super().__init__()
        root_path = Path(os.path.realpath(__file__)).parent
        self.config_dir = Path(root_path).parent.joinpath('config')
        self.chia_config_file = self.config_dir.joinpath('chia_client.ini')

        self.__socket_type = None
        self.__server = None
        self.__port = None
        self.__socket_dir = None
        self.auth_hash = None
        self._check_log_and_config_path()

        self.load_config()

    @classmethod
    def __call__(cls, *args, **kwargs):
        print("In CALL")
        if cls not in cls._instances:
            cls._instances[cls] = super(NodeConfig, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

    def load_config(self):
        log.debug(f"self.chia_config_file: {self.chia_config_file}")

        self.read(self.chia_config_file)
        connection_info = self['Connection']

        self.__socket_type = format(connection_info["type"])
        self.__server = format(connection_info["server"])
        self.__port = format(connection_info["port"])
        self.__socket_dir = format(connection_info["socketdir"])
        self.auth_hash = format(self["NodeInfo"]["authhash"])

    def get_script_info(self):
        return self["ScriptInfo"]["version"]

    def get_connection(self):
        return f"{self.__socket_type}://{self.__server}:{self.__port}{self.__socket_dir}"

    def get_chia_path(self):
        return self["Chia"]["chiaactivatepath"]

    def get_chia_ports(self):
        return self["Chia"]

    def update_config(self, section, key, value):
        self[section][key] = value
        with open(self.chia_config_file, "w") as conf:
            self.write(conf)

        self.read(self.chia_config_file)

    def _check_log_and_config_path(self):
        log.info("Create config folder if not exits.")


        if not self.config_dir.exists():
            log.info(f"Config folder does not exists. Create: {self.config_dir}")
            os.makedirs(self.config_dir)

        if not self.chia_config_file.exists():
            log.info("Config file does not exists. Write default config.")
            self.write_default_config()
            log.info("Config file created. Please setup your config now. Exiting..")

            sys.exit(0)

    def write_default_config(self):
        default_config = {
            'ScriptInfo': {'version': version.__version__},
            'Connection': {
                'server': 'chiamgmt.example.com',
                'port': '443',
                'socketdir': '/chiamgmt',
                'type': 'wss'
            },
            'NodeInfo': {'authhash': ''},
            'Chia': {
                'chiaactivatepath': '',
                'walletservice': 'chia_wallet',
                'farmerservice': 'chia_farmer',
                'harvesterservice': 'chia_harvester'
            }
        }

        self.read_dict(default_config)

        # write config to file
        with open(self.chia_config_file, 'w+') as configfile:
            self.write(configfile)
