from pathlib import Path
from inspect import getsourcefile
import sys
import os
import logging
import asyncio
import traceback
import subprocess

import psutil

from node import __version__
from node.NodeConfig import NodeConfig
from node.ChiaHandler import ChiaHandler
from node.NodeLogger import NodeLogger
from node.NodeWebsocket import NodeWebsocket
from system.SystemInfo import IS_WINDOWS


__file__ = getsourcefile(lambda:0)
NodeLogger()
log = logging.getLogger()
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


async def main(websocket: NodeWebsocket):
    log.info(f"Node version: {__version__}")
    
    node_config = NodeConfig()

    # disallow run as root.
    if not IS_WINDOWS and os.geteuid() == 0:
        raise Exception("Run as root user not allowed!")

    chia_interpreter = ChiaHandler()
    chia_paths = await chia_interpreter.get_chia_paths()
    log.info(
        f"Starting ChiaNode python script Version: {node_config.get_script_info()} and "
        f"Chia Version: {chia_paths.get('version')}."
    )

    if already_running():
        log.info("An instance of this script is already running. Exiting...")
        exit(0)

    log.info("Starting websocket node.")

    await websocket.start()


def run():
    loop = asyncio.get_event_loop()
    ws = NodeWebsocket()

    try:
        loop.run_until_complete(main(ws))
    except KeyboardInterrupt:
        log.info("Ctrl+C was pressed. Node client stopped. Bye.")
    except Exception:
        log.error(traceback.format_exc())
    finally:
        # destroy tray icon on windows 
        # if the exit was not triggered by the tray icon, it may not have been closed yet
        if IS_WINDOWS:
            ws.destroy_tray()


if __name__ == "__main__":
    run()
