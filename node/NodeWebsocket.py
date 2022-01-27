import sys
import json
import logging
import traceback
import inspect
import time
from typing import Tuple, Any
from functools import partial
from pathlib import Path

from websocket import WebSocketApp
from websocket._exceptions import WebSocketConnectionClosedException

from node.ApiHandler import ApiHandler
from node.NodeConfig import NodeConfig

try:
    import thread
except ImportError:
    import _thread as thread


log = logging.getLogger()


class NodeWebsocket:

    def __init__(self):
        log.info(f"Websocket connection: {NodeConfig().get_connection()}")
        self.node_config = NodeConfig()

        on_message = partial(self.catch_exc_on_message)
        on_error = partial(self.on_error)
        on_close = partial(self.on_close)

        self.socket = WebSocketApp(
            NodeConfig().get_connection(),
            on_open=partial(self.on_open),
            on_message=on_message,
            on_error=on_error,
            on_close=on_close
        )

        self.thread_restart = False
        self.thread_closed = False
        self.stop_websocket = False

    @staticmethod
    def _json_serialize(obj: Any) -> Any:
        if isinstance(obj, Path):
            return obj.as_posix()

    def start_websocket(self, *args, **kwargs):
        """Starts a new Websocket."""

        log.debug(f"inspect.stack()[1][3]: {inspect.stack()[1][3]}")
        self.thread_restart = False

        if not self.stop_websocket:
            #websocket.enableTrace(True)
            self.socket.run_forever(ping_interval=5)

    def catch_exc_on_message(self, *args, **kwargs):
        """Runs self._on_message() and catch raised exceptions."""

        log.debug(f"args: {args}")
        log.debug(f"len(args): {len(args)}")
        try:
            self._on_message(*args, **kwargs)
        except Exception:
            log.exception(traceback.format_exc())

    def _on_message(self, websocket: WebSocketApp, message: str) -> None:
        """Receives the incomming socket data.

        Args:
            websocket (WebSocketApp): Current WebSocketApp instance.
            message (str): Recived message from Server.
        """

        command = json.loads(message)

        if self.node_config.auth_hash and command.keys() and int(command.get(list(command.keys())[0], {}).get('status')) > 0:
            log.debug(command)
            return

        api_result = ApiHandler(self.socket).handle(command)

        log.debug(f"api_result: {api_result}")
        try:
            if api_result is not None:
                if 0 in api_result:
                    for key in api_result:
                        try:
                            websocket.send(
                                json.dumps(api_result[key])
                            )
                        except Exception:
                            log.exception(traceback.format_exc())
                else:
                    websocket.send(json.dumps(api_result, default=self._json_serialize))
        except Exception:
            log.exception(traceback.format_exc())

    def on_error(self, websocket, error, *args, **kwargs):
        log.error("Websocket node closed unexpected.")
        log.error(error)
        if error and hasattr(error, 'status_code'):
            log.error(f"{error.status_code}: {error}")

            if error.status_code >= 400:
                log.error(f"Critical websocket or server error, wait 15 seconds before continue.")
                time.sleep(15)

        if self.stop_websocket or self.thread_restart:
            websocket.close()

    def on_close(self, websocket, error, *args, **kwargs):
        """Close the Application or restart the websocket on error.

        Args:
            websocket (WebsSocketApp): Current WebSocketApp instance.
            error (str): Occoured error message.
        """
        log.error("Websocket node closed.")
        log.error(f"error: {error}")        
        
        if self.stop_websocket:
            self.thread_closed = True
            sys.exit(0)

        # wait 5 sec to prevent a stack overflow
        time.sleep(.5)
        self.thread_restart = True
        self.start_websocket()
                

    def on_open(self, *args, **kwargs) -> None:
        """Waits for login on Server."""

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
        """Get the Node login status from defined Server

        Returns:
            Tuple[bool, dict]: Login status and message from server.
        """

        log.debug(f"Using auth_hash: {NodeConfig().auth_hash}")
        login_result = {}
        data = json.dumps(
            {
                "node": {
                    'nodeinfo': {'hostname': NodeConfig().hostname},
                    'socketaction': "ownRequest"
                },
                'request': {
                    'data': [],
                    'logindata': { 'authhash': NodeConfig().auth_hash},
                    'backendInfo': { 
                        'namespace': "ChiaMgmt\\Nodes\\Nodes_Api",
                        'method': "loginStatus" }
                }
            }
        )

        try:
            self.socket.send(data)
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
        auth_hash = login_result['loginStatus']['data'].get('authhash')
        if login_status_code in ["010005006", "010005013"] or auth_hash is not None and self.node_config.auth_hash != login_result['loginStatus']['data']['authhash']:
            log.info("Got new auth hash! Write to config.")
            try:
                self.node_config.update_config("node", "authhash", login_result['loginStatus']['data']['authhash'])
            except Exception:
                log.error(traceback.format_exc())
            log.debug(f"New auth_hash: {self.node_config.auth_hash}")


        elif login_status_code == 0:
            return True, login_result
        
        return False, login_result
