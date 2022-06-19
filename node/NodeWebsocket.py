import sys
import json
import logging
from threading import Lock
import traceback
import time
import asyncio
from typing import Any
from pathlib import Path

import websockets

from node.ApiHandler import ApiHandler
from node.NodeConfig import NodeConfig
from system.SystemInfo import IS_WINDOWS
if IS_WINDOWS:
    from node.tray_icon.TrayIcon import TrayIcon


log = logging.getLogger()
logging.getLogger("websockets").setLevel(logging.DEBUG)

class NodeWebsocket():
    def __init__(self) -> None:
        self._conn = websockets.connect(NodeConfig().get_connection())
        self.socket = None

        self.node_config = NodeConfig()
        self.api_handler = ApiHandler()

        self.stop_lock = Lock()
        self._stop_websocket = False
        if IS_WINDOWS:
            self.tray_icon = None

    @property
    def stop_websocket(self):
        return self._stop_websocket

    @stop_websocket.setter
    def stop_websocket(self, value: bool):
        with self.stop_lock:
            self._stop_websocket = value

    async def __aexit__(self, *args, **kwargs):
        await self.close()

    async def close(self) -> None:
        await self._conn.__aexit__(*sys.exc_info())

    async def send(self, message: Any):
        await self.socket.send(message)

    async def receive(self) -> str:
        return await self.socket.recv()

    async def _ping(self) -> None:
        """Sends a 0 byte Frame to keep alive. 
        
        This is required because the normal keepalive ping/pong is not enough
        to keep the connection alive.
        """
        while not self.stop_websocket:
            log.info("Send keep alive.")
            try:
                await self.send('')
                await asyncio.sleep(10)
            except AttributeError:
                break

    async def connect(self, is_reconnect: bool = False) -> None:
        """Creates a connection to server and do login.

        Args:
            is_reconnect (bool, optional): If is reconnect. Defaults to False.
        """
        
        if self.socket:
            if is_reconnect and self.socket.open:
                await self.close()

        self.socket = None
        error_count = 0
        while self.socket is None and not self.stop_websocket:
            try:
                self.socket = await self._conn.__aenter__()
                error_count = 0
            except (websockets.exceptions.InvalidStatusCode, asyncio.exceptions.TimeoutError):
                error_count += 1

                # prevent error logging spam
                if self.stop_websocket or error_count == 1 or error_count % 10 == 0:
                    return

                log.error("Could not reach server websocket!")
                log.exception(traceback.format_exc())
                await asyncio.sleep(1)
            except asyncio.exceptions.CancelledError:
                if self.stop_websocket:
                    return
            except Exception:
                log.exception(traceback.format_exc())
                await asyncio.sleep(5)

        await self._login()

    def destroy_tray(self):
        if IS_WINDOWS:
            self.tray_icon.destroy()

    async def _create_tray(self):
        """Crate tray icon on Windows."""
        if not IS_WINDOWS:
            return

        self.tray_icon = TrayIcon(websocket_instance=self)
        self.tray_icon.start()

    async def _login(self):
        log.info("Login..")
        while not await self.get_login_status() and not self.stop_websocket:
            log.info("Waiting for login on server..")
            time.sleep(5)
        
        log.info("Node login was successful.")

    async def start(self):
        if IS_WINDOWS:
            await self._create_tray()
        await self.connect()

        # create paralel task for keepalive ping
        asyncio.create_task(self._ping())

        while not self.stop_websocket:        
            try:
                recived_data = await self.receive()
                asyncio.create_task(self._on_message(recived_data))
            except websockets.exceptions.ConnectionClosedOK:
                await self.connect(is_reconnect=True)
            except Exception:
                if self.stop_websocket:
                    break
                else:
                    await self.connect(is_reconnect=True)


    @staticmethod
    def _json_serialize(obj: Any) -> Any:
        if isinstance(obj, Path):
            return obj.as_posix()

    async def _on_message(self, message: str) -> None:
        """Receives the incomming socket data.

        Args:
            websocket (WebSocketApp): Current WebSocketApp instance.
            message (str): Recived message from Server.
        """
        if self.stop_websocket:
            return

        log.debug(message)

        command = json.loads(message)

        if not message and self.node_config.auth_hash and command.keys() and int(command.get(list(command.keys())[0], {}).get('status')) > 0:
            log.debug(command)
            return

        log.debug(f"command: {command}")
        api_result = await self.api_handler.handle(command)

        log.debug(f"api_result: {api_result}")
        try:
            if api_result is not None:
                if 0 in api_result:
                    for key in api_result:
                        try:
                            await self.send(
                                json.dumps(api_result[key])
                            )
                        except Exception:
                            log.exception(traceback.format_exc())
                else:
                    await self.send(json.dumps(api_result, default=self._json_serialize))
        except Exception:
            log.exception(traceback.format_exc())

    async def get_login_status(self) -> bool:
        """Get the Node login status from defined Server

        Returns:
            bool: True if client is logged in
        """

        if self.stop_websocket:
            return

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
            await self.send(data)
            login_result = json.loads(await self.receive())
        except Exception:
            if not self.stop_websocket:
                log.exception(traceback.format_exc())
            return False

        log.debug(f"login status: {login_result}")
        login_status_code = login_result['loginStatus']['status']

        # 010005002 = This node is waiting for authentication
        # 010005006 = got a auth hash
        # 010005013 = node exists but auth hash is not in node.ini
        auth_hash = login_result['loginStatus']['data'].get('authhash')
        if login_status_code in ["010005006", "010005013"] or auth_hash is not None and self.node_config.auth_hash != login_result['loginStatus']['data']['authhash']:
            log.info("Got new auth hash! Write to config.")
            try:
                self.node_config.update_config(
                    "Node", "authhash", 
                    login_result['loginStatus']['data']['authhash'], 
                    reload=True
                )
            except Exception:
                log.error(traceback.format_exc())
            log.debug(f"New auth_hash: {self.node_config.auth_hash}")

        elif login_status_code == 0:
            return True
        
        return False
