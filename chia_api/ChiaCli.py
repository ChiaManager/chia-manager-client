from subprocess import Popen, PIPE

from system.SystemInfo import IS_WINDOWS
from node.NodeConfig import NodeConfig

class ChiaCli:

    @staticmethod
    def run_chia_command(command: str) -> tuple:
        if IS_WINDOWS:
            return Popen(
                [str(NodeConfig().chia_path), command],
                stdout=PIPE,
                stderr=PIPE
            ).communicate()
        else:
            return Popen(
                [f"source {NodeConfig().chia_path}", '&&', 'chia', command, '&&', 'deactivate'],
                shell=True,
                executable='/bin/bash',
                stdout=PIPE,
                stderr=PIPE
            ).communicate()