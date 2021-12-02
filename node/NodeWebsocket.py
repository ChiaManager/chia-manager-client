import sys
import json
import logging
import traceback
import inspect
from typing import Tuple
from functools import partial

import websocket as websocket
from websocket._exceptions import WebSocketConnectionClosedException

from node.ApiHandler import ApiHandler
from node.NodeConfig import NodeConfig
from node.NodeHelper import NodeHelper

try:
    import thread
except ImportError:
    import _thread as thread
    import time


log = logging.getLogger()


class NodeWebsocket:

    def __init__(self):
        log.info(f"Websocket connection: {NodeConfig().get_connection()}")
        self.node_config = NodeConfig()

        on_message = partial(self.catch_exc_on_message)
        on_error = partial(self.on_error)
        on_close = partial(self.on_close)

        self.socket = websocket.WebSocketApp(
            NodeConfig().get_connection(),
            on_open=partial(self.on_open),
            on_message=on_message,
            on_error=on_error,
            on_close=on_close
        )

        self.thread_restart = False
        self.thread_closed = False
        self.stop_websocket = False


    def start_websocket(self, *args, **kwargs):
        log.debug(f"inspect.stack()[1][3]: {inspect.stack()[1][3]}")
        self.thread_restart = False

        if not self.stop_websocket:
            #websocket.enableTrace(True)
            self.socket.run_forever(ping_interval=5)

    def catch_exc_on_message(self, *args, **kwargs):
        log.debug(f"args: {args}")
        log.debug(f"len(args): {len(args)}")
        try:
            self._on_message(*args, **kwargs)
        except Exception:
            log.exception(traceback.format_exc())

    def _on_message(self, ws, message):
        command = json.loads(message)

        if self.node_config.auth_hash and command.keys() and int(command.get(list(command.keys())[0], {}).get('status')) > 0:
            log.debug(command)
            return

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
        if error and hasattr(error, 'status_code'):
            log.error(f"{error.status_code}: {error}")

            if error.status_code >= 400:
                log.error(f"Critical websocket or server error, wait 15 seconds before continue.")
                time.sleep(15)

        if self.stop_websocket or self.thread_restart:
            ws.close()

    def on_close(self, ws, error, *args, **kwargs):
        log.error("Websocket node closed.")
        log.error(f"error: {error}")        
        
        if self.stop_websocket:
            self.thread_closed = True
            sys,exit(0)

        # wait 5 sec to prevent a stack overflow
        time.sleep(.5)
        self.thread_restart = True
        self.start_websocket()
                

    def on_open(self, ws) -> None:
        while not self.get_login_status()[0]:
            log.info("Waiting for login on server..")
            time.sleep(5)
        
        if self.thread_restart:
            self.socket.close()
            log.debug(f"self.thread_restart: {self.thread_restart}")
            try:
                while not self.thread_closed:
                    log.debug(f"Thread not closed.. wait 6 seconds and check again..")
                    time.sleep(6)
                
                self.thread_closed = False
            except KeyboardInterrupt:
                exit(0)
                

    def get_login_status(self) -> Tuple[bool, dict]:
        login_result = {}

        try:
            self.socket.send( 
                json.dumps(
                    NodeHelper.get_formated_info(
                        NodeConfig().auth_hash or "", "ownRequest", "ChiaMgmt\\Nodes\\Nodes_Api", "Nodes_Api", "loginStatus", {}
                    )
                )
            )
            login_result = json.loads(self.socket.sock.recv())
        except WebSocketConnectionClosedException:
            self.start_websocket()
        except Exception:
            log.exception(traceback.format_exc())
            return False, {}

        log.debug(f"login status: {login_result}")
        login_status_code = login_result['loginStatus']['status']

        # 010005002 = This node is waiting for authentication
        # 010005006 = got a auth hash
        # 010005013 = node exists but auth hash is not in node.ini
        if login_status_code in ["010005006", "010005013"] and not self.node_config.auth_hash:
            log.info("Got new auth hash! Write to config.")
            self.node_config.update_config("node", "authhash", login_result['loginStatus']['data']['newauthhash'])    

        elif login_status_code == 0:
            return True, login_result
        
        return False, login_result
 

    def run(self, *args):
        log.debug("Start websocket")
        while True:                
            if (self.thread_restart and not self.stop_websocket) or self.stop_websocket:
                log.debug("Closing thread..")
                self.thread_closed = True
                exit(0)
                
            time.sleep(5)
            
        run_with_self = partial(run, self)
        thread.start_new_thread(run_with_self, ())
        
