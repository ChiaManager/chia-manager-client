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

    def get_wallet_info(self):
        log.debug("in get_wallet_info")
        data = {}

        log.debug(f"wallet_status: {self.get_wallet_status()}")
        if not (self.chia_paths_exist and self.get_wallet_status()):
            return data

        return data
        log.debug(f"self.format_chia_command('chia wallet show'): {self.format_chia_command('chia wallet show')}")
        try:
            wallet_infos, stderr = subprocess.Popen(
                #'source /home/test/chia-blockchain/activate && chia wallet show && deactivate',
                #"source /home/test/chia-blockchain/activate && chia version",
                self.format_chia_command('chia wallet show'),
                executable='/bin/bash', stdout=subprocess.PIPE, stderr=subprocess.PIPE
            ).communicate()

            if stderr:
                log.exception(stderr.decode('utf-8'))
                return data
        except Exception:
            log.exception(traceback.format_exc())
            return data

        log.debug(f"wallet_infos: {wallet_infos.decode('utf-8')}")

        temp_data = {}
        count = 0
        for line in wallet_infos:
            if "Wallet height" in line:
                temp_data["walletheight"] = line.split(":")[1].strip()
            elif "Sync status" in line:
                temp_data["syncstatus"] = line.split(":")[1].strip()
            elif "Wallet ID" in line:
                temp_data["walletid"] = line.split()[2].strip()
                temp_data["wallettype"] = line.split()[4].strip()
            elif "-Total Balance" in line.strip():
                temp_data["totalbalance"] = line.split()[2].strip()
            elif "-Pending Total" in line.strip():
                temp_data["pendingtotalbalance"] = line.split()[3].strip()
            elif "-Spendable" in line.strip():
                temp_data["spendable"] = line.split()[1].strip()
                temp_data["walletaddress"] = \
                    os.popen(self.format_chia_command("chia wallet get_address")).read().splitlines()[count]
                data["wallet"] = {}
                data["wallet"][temp_data["walletid"]] = temp_data
                temp_data = {}
                count = 1

        log.debug(f"wallet_info: {data}")
        return data

    def get_farmer_info(self) -> dict:

        if not (self.chia_paths_exist and self.get_farmer_status()):
            return {}

        farm_summary_command = self.format_chia_command("chia farm summary")
        log.debug(farm_summary_command)
        farmer_info = os.popen(self.format_chia_command("chia farm summary")).read().splitlines()

        log.debug(f"farmer_info: {farmer_info}")
        farmer_info_mapping = {
            'farming_status': None,
            'total_chia_farmed': None,
            'user_transaction_fees': None,
            'block_rewards': None,
            'last_height_farmed': None,
            'plot_count': None,
            'total_size_of_plots': None,
            'estimated_network_space': None,
            'expected_time_to_win': None,
        }
        farmer_info_data = {}
        for line in farmer_info:
            line = line.split(":")[1].strip()
            log.debug(f"line: {line}")

            try:
                key = line.lower().replace(' ', '_').split(':')[0]
            except Exception:
                log.exception(traceback.format_exc())
                continue

            if farmer_info_mapping.get(key):
                farmer_info_data[key] = line

        farmer_info_data["challenges"] = os.popen(self.format_chia_command("chia farm challenges")).read().splitlines()
        log.debug(f"farmer_info_data: {farmer_info_data}")

        return {'farm': farmer_info_data}

    def get_harvester_info(self) -> dict:

        log.debug(f"self.check_chia_paths(): {self.check_chia_paths()}")
        log.debug(f"self.get_harvester_status(): {self.get_harvester_status()}")

        result = {'harvester': {}}
        if self.check_chia_paths() and self.get_harvester_status():
            plot_dirs = os.popen(self.format_chia_command("chia plots show | tail -n +5")).read().splitlines()
            log.debug(f"plot_dirs: {plot_dirs}")
            filesystems = subprocess.run("df -h | tail -n +2", stdout=subprocess.PIPE, shell=True)
            log.debug(filesystems)
            filesystemdecoded = filesystems.stdout.decode('UTF-8').splitlines()
            log.debug(f"len(filesystemdecoded): {len(filesystemdecoded)}")
            log.debug(f"filesystemdecoded: {filesystemdecoded}")

            for filesystem in filesystemdecoded:
                filesystemsplitted = list(filter(None, filesystem.split(" ")))
                if filesystemsplitted[5] != "/" and any(filesystemsplitted[5] in string for string in plot_dirs):
                    plotdirindex = [plot_dirs.index(i) for i in plot_dirs if filesystemsplitted[5] in i]
                    plotdirname = plot_dirs[plotdirindex[0]]

                    result["harvester"][plotdirname] = {
                        'devname': filesystemsplitted[0],
                        'totalsize': filesystemsplitted[1],
                        'totalused': filesystemsplitted[2],
                        'totalusedpercent': filesystemsplitted[4],
                        'mountpoint': filesystemsplitted[5],
                        'finalplotsdir': plot_dirs[plotdirindex[0]],
                    }

                    plotcountproc = subprocess.run(
                        "ls -al {} | egrep '*.plot' | wc -l".format(plot_dirs[plotdirindex[0]]),
                        stdout=subprocess.PIPE, shell=True
                    )
                    result["harvester"][plotdirname]["plotcount"] = int(plotcountproc.stdout.decode('UTF-8').strip())

                    foundplots = {}
                    if (result["harvester"][plotdirname]["plotcount"] > 0):
                        foundplots = subprocess.Popen("ls {} | egrep '*.plot'".format(plot_dirs[plotdirindex[0]]),
                                                      shell=True, stdout=subprocess.PIPE)
                        foundplots = foundplots.stdout.read().decode('UTF-8').splitlines()

                    result["harvester"][plotdirname]["plotsfound"] = foundplots

            for plot_dir in plot_dirs:
                if plot_dir not in result["harvester"]:
                    result["harvester"][plot_dir] = {}

        log.debug(f"harvester_info: {result}")
        return result

    def get_wallet_status(self, as_dict: bool = False):
        log.info("Checking if wallet service is running.")
        service_result = subprocess.run(
            f"ps -aux | grep chia_wallet| grep -v 'grep'", shell=True
        )

        if service_result.returncode == 0:
            log.info("Wallet service running.")
            return True if not as_dict else {"status": 0, "message": "Wallet service running."}

        log.warning("Wallet service not running.")
        return False if not as_dict else {"status": 1, "message": "Wallet service not running."}

    def get_farmer_status(self, as_dict: bool = False) -> Union[dict, bool]:
        log.info("Checking if farmer service is running.")
        service_result = subprocess.run(
            f"ps -aux | grep chia_farmer | grep -v 'grep'", shell=True
        )

        if service_result.returncode == 0:
            log.info("Farmer service running.")

            if as_dict:
                return {"status": 0, "message": "Farmer service running."}
            return True

        log.warning("Farmer service not running.")

        if as_dict:
            return {"status": 1, "message": "Farmer service not running."}
        return False

    def get_harvester_status(self, as_dict: bool = False) -> Union[bool, dict]:
        log.info("Checking if harvester service is running.")
        service_result = subprocess.run(
            f"ps -aux | grep chia_harvester | grep -v 'grep'", shell=True
        )

        if service_result.returncode == 0:
            log.info("Harvester service running.")

            if as_dict:
                return {"status": 0, "message": "Harvester service running."}
            return True

        log.warning("Harvester service not running.")

        if as_dict:
            return {"status": 1, "message": "Harvester service not running."}
        return False

    def restart_farmer(self) -> dict:
        if self._restart_service('farmer'):
            return self.get_farmer_status(as_dict=True)

        return {}

    def restart_wallet(self):
        if self._restart_service('wallet'):
            return self.get_wallet_status(as_dict=True)

        return {}

    def restart_harvester(self) -> dict:
        if self._restart_service('harvester'):
            return self.get_harvester_status(as_dict=True)

        return {}

    def _restart_service(self, service_name) -> bool:
        log.info(f"Restarting {service_name} service.")

        stdout, stderr = self.run_chia_command(f"start {service_name} -r")

        if not stderr:
            log.info(f"Restarting {service_name} service. Done!")
            return True

        log.error(f"Failed to restart {service_name}. Error: {stderr}")
        return False

    def run_chia_command(self, command: str) -> tuple:
        return subprocess.Popen(
            [f"source {self.chia_venv_activation_path}", '&&', 'chia', command, '&&', 'deactivate'],
            shell=True,
            executable='/bin/bash',
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        ).communicate()

    def format_chia_command(self, command):
        return f"source {self.chia_venv_activation_path} && {command} && deactivate"


if __name__ == '__main__':
    NodeLogger(logging.DEBUG, True)
    print(ChiaHandler().get_harvester_info())
