import logging
import os
import json
import sys
import traceback

import psutil
import subprocess
from pathlib import Path

from node import __version__
from node.NodeConfig import NodeConfig
from classes.FirstStartWizard import FirstStartWizard
from node.ChiaHandler import ChiaHandler
from node.NodeLogger import NodeLogger
from node.NodeWebsocket import NodeWebsocket

NodeLogger()
log = logging.getLogger()
node_config = NodeConfig()

interrupt = False


def already_running():
    num_instance = 0
    for q in psutil.process_iter():
        if 'python' in q.name():
            if len(q.cmdline()) > 1 and os.path.basename(__file__) in q.cmdline()[1]:
                num_instance += 1
    return num_instance > 1


def restart_script():
    log.info("This script will be restarted in background in 5sec.")
    subprocess.Popen(['python', Path(os.path.realpath(__file__))], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    sys.exit()


def main():
    log.info(f"Node version: {__version__}")
    
    # disallow run as root.
    if os.geteuid() == 0:
        raise Exception("Run as root user not allowed!")

    chia_version, _ = subprocess.Popen(
        r'. /home/test/chia-blockchain/activate && chia wallet show && deactivate',
        start_new_session=True,
        shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    ).communicate()

    first_start_wizard = FirstStartWizard()
    chia_interpreter = ChiaHandler()
    log.info(
        f"Starting ChiaNode python script Version: {node_config.get_script_info()} and "
        f"Chia Version: {chia_interpreter.get_chia_paths().get('version')}."
    )

    if already_running():
        log.info("An instance of this script is already running. Ignoring...")
    log.info("Starting websocket node.")

    if not node_config.auth_hash:
        first_start_wizard.setFirstStart(True)
        first_start_wizard.step1()

    NodeWebsocket().start_websocket()


if __name__ == "__main__":

    try:
        main()
    except KeyboardInterrupt:
        log.info("Ctrl+C was pressed. Stopping Script. Bye.")
    except Exception:
        log.error(traceback.format_exc())
    finally:
        interrupt = True