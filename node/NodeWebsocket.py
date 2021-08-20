import json
import logging
import traceback
from functools import partial

import websocket as websocket

from classes.FirstStartWizard import FirstStartWizard
from node.ApiHandler import ApiHandler
from node.NodeConfig import NodeConfig
from node.NodeHelper import NodeHelper

try:
    import thread
except ImportError:
    import _thread as thread
    import time

firstStartWizard = FirstStartWizard()

log = logging.getLogger()
stop_websocket = False


class NodeWebsocket:

    def __init__(self):
        log.info(f"Websocket connection: {NodeConfig().get_connection()}")

        on_message = partial(self.catch_exc_on_message)

        self.socket = websocket.WebSocketApp(
            NodeConfig().get_connection(),
            on_open=self.on_open,
            on_message=on_message,
            on_error=self.on_error,
            on_close=self.on_close
        )

    def start_websocket(self, *args, **kwargs):
        self.socket.run_forever()

    def catch_exc_on_message(self, *args, **kwargs):
        log.debug(f"args: {args}")
        log.debug(f"len(args): {len(args)}")
        try:
            self._on_message(*args, **kwargs)
        except Exception:
            log.exception(traceback.format_exc())

    def _on_message(self, ws, message):

        command = json.loads(message)

        log.debug(f"command: {command}")
        log.debug(f"command: {command.keys()}")
        log.debug(f"command.get(list(command.keys())[0]).get('status'): {command.get(list(command.keys())[0], {}).get('status') } ")
        if command.keys() and command.get(list(command.keys())[0], {}).get('status') > 0:
            log.debug(command)
            return

        log.debug(f"command: {command}")
        if firstStartWizard.getFirstStart():
            key = list(command.keys())[0]
            log.debug(command)
            log.info(f"Got message from API on command {key}: {command[key]}")

            if firstStartWizard.current_step == 2:
                if firstStartWizard.step2(command):
                    log.info("Finished init wizard successfully. Waiting for authentication on backend.")
                    ws.send(
                        json.dumps(
                            NodeHelper.get_formated_info(
                                NodeConfig().auth_hash, "ownRequest", "ChiaMgmt\\Nodes\\Nodes_Api", "Nodes_Api",
                                "loginStatus", {}
                            )
                        )
                    )
                else:
                    log.info("An error occurred during first start init")
            elif firstStartWizard.getFirststartStep() == 3:
                if firstStartWizard.step3(command):
                    log.info("Finished authentication successfully. Please refer to above message.")
                    firstStartWizard.setFirstStart(False)
                else:
                    log.error("An error occurred interpreting request string from api.")
        else:
            api_result = ApiHandler(self.socket).interpretCommand(command)
            log.debug(f"api_result: {api_result}")
            try:
                if api_result is not None:
                    if 0 in api_result:
                        for key in api_result:
                            try:
                                ws.send(
                                    json.dumps(api_result[key])
                                )
                            except Exception:
                                log.exception(traceback.format_exc())
                    else:
                        ws.send(json.dumps(api_result, default=NodeHelper.json_serialize))
            except Exception:
                log.exception(traceback.format_exc())

    @staticmethod
    def on_error(ws, error, *args, **kwargs):
        log.error("Websocket node closed unexpected.")
        log.error(error)
        if not stop_websocket:
            ws.close()

    @staticmethod
    def on_close(ws, error, *args, **kwargs):
        log.error("Websocket node closed.")
        log.error(f"error: {error}")

    @staticmethod
    def on_open(ws):
        auth_hash = ""
        if not firstStartWizard.getFirstStart():
            auth_hash = NodeConfig().auth_hash

        log.info("Requesting login information from api.")
        try:
            ws.send(
                json.dumps(
                    NodeHelper.get_formated_info(
                        auth_hash, "ownRequest", "ChiaMgmt\\Nodes\\Nodes_Api", "Nodes_Api", "loginStatus", {}
                    )
                )
            )
        except Exception:
            log.exception(traceback.format_exc())

        def run(*args):
            while True:
                time.sleep(5)

        thread.start_new_thread(run, ())
