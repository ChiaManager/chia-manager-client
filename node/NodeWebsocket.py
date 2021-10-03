import json
import logging
import traceback
import inspect
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


class NodeWebsocket:

    def __init__(self):
        log.info(f"Websocket connection: {NodeConfig().get_connection()}")
        self.thread_restart = False
        self.thread_closed = False
        self.stop_websocket = False

        on_message = partial(self.catch_exc_on_message)
        # on_open = 
        on_error = partial(self.on_error)
        on_close = partial(self.on_close)

        self.socket = websocket.WebSocketApp(
            NodeConfig().get_connection(),
            on_open=partial(self.on_open),
            on_message=on_message,
            on_error=on_error,
            on_close=on_close
        )

    def start_websocket(self, *args, **kwargs):
        log.debug(f"inspect.stack()[1][3]: {inspect.stack()[1][3]}")
        if not self.stop_websocket:
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
        if command.keys() and int(command.get(list(command.keys())[0], {}).get('status')) > 0:
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

    def on_error(self, ws, error, *args, **kwargs):
        log.error("Websocket node closed unexpected.")
        log.error(error)
        if not self.stop_websocket:
            ws.close()

    def on_close(self, ws, error, *args, **kwargs):
        log.error("Websocket node closed.")
        log.error(f"error: {error}")
        if not self.stop_websocket:
            self.thread_restart = True
            self.start_websocket()
        else:
            exit(0)
                

    def on_open(self, ws):            
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

        if self.thread_restart:
            log.debug(f"self.thread_restart: {self.thread_restart}")
            try:
                while not self.thread_closed:
                    log.debug(f"Thread not closed.. wait 6 seconds and check again..")
                    time.sleep(6)
                
                self.thread_closed = False
                self.thread_restart = False
            except KeyboardInterrupt:
                exit(0)
                
        def run(self, *args):
            log.debug("run run")
            while True:                
                if (self.thread_restart and not self.stop_websocket) or self.stop_websocket:
                    log.debug("Closing thread..")
                    self.thread_closed = True
                    exit(0)
                    
                time.sleep(5)
                
        run_with_self = partial(run, self)
        thread.start_new_thread(run_with_self, ())
        
