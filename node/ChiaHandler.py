# /bin/bash
import os
import logging
import subprocess
import sys
import traceback
from pathlib import Path
from typing import Union
from chia_api.ChiaDaemon import ChiaDaemon

from node.NodeConfig import NodeConfig
from node.NodeLogger import NodeLogger
from system.SystemInfo import IS_WINDOWS

log = logging.getLogger()


class ChiaHandler:
    def __init__(self):
        self.chia_paths_exist = False
        self.node_config = NodeConfig()

        self.chia_cli_file = self.node_config.get("Chia", "chia_blockchain_cli")
        
        if not IS_WINDOWS and os.path.exists("/usr/bin/chia"):
            self.chia_cli_file = "/usr/bin/chia"
        elif not IS_WINDOWS and self.chia_cli_file:
            self.chia_cli_file = self.chia_cli_file.joinpath('activate')

        self.check_chia_paths()

    def check_chia_paths(self):
        log.info(f"Checking chia path: '{self.chia_cli_file}'")

        if self.chia_cli_file is None or not os.path.exists(self.chia_cli_file):
            log.error(f"Could not find Chia path: {self.chia_cli_file}")
            log.error(f"Please set [Chia][chia_path] in your node.ini.")

            if not IS_WINDOWS:
                log.error(f"The Default path should be something like '{Path.home().joinpath('chia-blockchain')}'")
            else:
                log.error("The Default path should be something like:")
                log.error(rf"{Path.home()}\AppData\Local\chia-blockchain\app-1.2.11\resources\app.asar.unpacked\daemon\chia.exe")
            
            sys.exit(0)

        if not IS_WINDOWS and not os.path.exists("/usr/bin/chia"):
            # check if chia .activate file exists (linux)
            if self.chia_venv_activation_path and not self.chia_venv_activation_path.is_file():
                log.error("Activate file not found. Did you installed chia-blockchain?")
                log.error(f"path: {self.chia_venv_activation_path}")
                sys.exit(0)

        self.chia_paths_exist = True
        return True

    async def get_chia_paths(self):
        return {
            'version': await ChiaDaemon().get_chia_version(),
            'path': self.chia_cli_file
        }

        if not self.chia_paths_exist:
            log.debug(f"self.chia_paths_exist: {self.chia_paths_exist}")
            return {}

        chia_version, _ = subprocess.Popen(
            self.format_chia_command('chia version'),
            shell=True, executable=r'/bin/bash', stdout=subprocess.PIPE, stderr=subprocess.PIPE
        ).communicate()

        log.info(f"chia_version: {chia_version.decode('utf-8')}")
        return {
            'version': chia_version.decode('utf-8'),
            'path': self.chia_venv_activation_path
        }

    def format_chia_command(self, command):
        return f"source {self.chia_venv_activation_path} && {command} && deactivate"
