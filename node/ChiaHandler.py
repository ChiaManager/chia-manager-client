# /bin/bash
import os
import logging
import subprocess
import sys
import traceback
from pathlib import Path
from typing import Union

from node.NodeConfig import NodeConfig
from node.NodeLogger import NodeLogger

log = logging.getLogger()


class ChiaHandler:
    def __init__(self):
        self.chia_paths_exist = False
        self.node_config = NodeConfig()

        self.chia_path = Path(self.node_config["Chia"]["chia_blockchain_path"])
        log.info(repr(self.node_config))
        self.chia_venv_activation_path = self.chia_path.joinpath('activate')

        self.check_chia_paths()

    def check_chia_paths(self):
        log.info(f"Checking activate path '{self.chia_venv_activation_path}'")

        log.info(f"self.chia_venv_activation_path: {self.chia_venv_activation_path.absolute()}")
        # check if chia .activate file exists
        if not self.chia_venv_activation_path.is_file():
            log.error("Activate file not found. Did you installed chia-blockchain?")
            sys.exit(0)

        self.chia_paths_exist = True
        return True

    def get_chia_paths(self):
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
