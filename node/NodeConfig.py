import sys
import os
import socket
import logging
from inspect import getsourcefile
from typing import Union, Any
from pathlib import Path
from ast import literal_eval
from configparser import ConfigParser, NoSectionError

from node import __version__
from system.SystemInfo import IS_WINDOWS

log = logging.getLogger()


class NodeConfig(ConfigParser):
    _instances = {}

    def __init__(self):
        super().__init__(allow_no_value=True)
        root_path = Path(getsourcefile(lambda:0)).parent.absolute()
        self.config_dir = Path(root_path).parent.joinpath('config')
        self.chia_config_file = self.config_dir.joinpath('node.ini')

        self.hostname = socket.gethostname()
        self.__server = None
        self.__port = None
        self.__socket_dir = None
        self.auth_hash = None
        self.chia_blockchain_cli = None
        self.logging = {}
        self.key_convert_map = {
            'server': str,
            'socketdir': str,
            'chia_blockchain_cli': Path,
            'log_path': Path,
            'authhash': str, 
            'log_level': lambda level : logging._nameToLevel[level]  if level.isalpha() else int(level)
        }

        self._check_log_and_config_path()
        self.load_config()
 
    @classmethod
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(NodeConfig, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

    def __getitem__(self, key):
        if key != self.default_section and not self.has_section(key):
            return None

        return self._proxies[key]

    def _write_default_config(self):
        print("Write default config..")
        self.update_config('Connection', 'server', '127.0.0.1', False)
        self.update_config('Connection', 'port', 443, False)
        self.update_config('Connection', 'socketdir', '/chiamgmt', False)
        self.update_config('Chia', 'chia_blockchain_cli', self._get_chia_cli_path(), False)
        self.update_config('Logging', 'log_level', logging.ERROR, False)

        print("Write default config.. Done!")

    def load_config(self):              
        log.debug(f"self.chia_config_file: {self.chia_config_file}")

        self.read(self.chia_config_file)
        connection_info = self['Connection']

        self.__server = format(connection_info["server"])
        self.__port = format(connection_info["port"])
        self.__socket_dir = format(connection_info["socketdir"])
        
        if self.has_option('Node', 'authhash'):
            self.auth_hash = format(self["Node"]["authhash"])

        if self.has_option('Chia','chia_blockchain_cli'):
            self.chia_blockchain_cli = format(self["Chia"]["chia_blockchain_cli"])
        else:
            cli_path = self._get_chia_cli_path()
            self.update_config('Chia','chia_blockchain_cli', cli_path)
            self.chia_blockchain_cli = cli_path
        
        # log config
        self.logging = self['Logging']


    def get(self, section: str, option: str, *, raw: bool = False, vars=None, fallback: Any = None) -> Union[Any, None]:

        try:
            d = self._unify_values(section, vars)
        except NoSectionError:
            return fallback

        option = self.optionxform(option)
        try:
            value = d[option]
        except KeyError:
            return fallback

        if raw or value is None:
            return value
        else:
            value = self._interpolation.before_get(self, section, option, value,d)

            if self.key_convert_map.get(option):
                return self.key_convert_map[option](value)

            return literal_eval(value)

    def get_script_info(self):
        return __version__

    def get_connection(self):
        return f"wss://{self.__server}:{self.__port}{self.__socket_dir}"

    def _get_chia_cli_path(self):
        if IS_WINDOWS and not self.has_option('Chia','chia_blockchain_cli'):
            for e in os.scandir(Path(os.getenv('LOCALAPPDATA'), 'chia-blockchain')):
                if e.is_dir() and e.name.startswith('app-'):
                    self.update_config('Chia','chia_blockchain_cli', Path(e.path, 'resources', 'app.asar.unpacked', 'daemon','chia.exe'), True)

        return self["Chia"]["chia_blockchain_cli"]

    def update_config(self, section: str, key: str, value: Any, reload: bool = True):
        log.debug("Write new config..")
        section = section.capitalize()
        # create section if not already exist
        if not self.has_section(section):
            self[section] = {}

        if type(value) == Path:
            value = str(value)

        self[section][key] = value
        with open(self.chia_config_file, "w") as conf:
            self.write(conf)

        log.debug("Write new config.. Done!")

        if reload:
            log.debug("Reload config..")
            self.load_config()
            log.debug("Reload config.. Done!")

    def _check_log_and_config_path(self):

        if not self.config_dir.exists():
            print(f"Config folder does not exists. Create: {self.config_dir}")
            os.makedirs(self.config_dir)

        if not self.chia_config_file.exists():
            print("Config file does not exists!")
            print(
                "Please configure your settings in node/node.ini \n" \
                "The sample file can be found at: node/example.node.ini"
            )

            self._write_default_config()
            sys.exit(0)
