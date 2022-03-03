import sys
import json
import logging
import traceback
import time
import asyncio
from typing import Any
from pathlib import Path

import websockets

from node.ApiHandler import ApiHandler
from node.NodeConfig import NodeConfig


log = logging.getLogger()
logging.getLogger("websockets").setLevel(logging.DEBUG)

class NodeWebsocket():
    def __await__(self):
        return self._async_init().__await__()

    async def _async_init(self) -> None:
        self._conn = websockets.connect(NodeConfig().get_connection())
        self.socket = None

        self.node_config = NodeConfig()
        self.stop_websocket = False

        return self

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
            await self.send('')
            await asyncio.sleep(25)

    async def connect(self, is_reconnect: bool = False) -> None:
        """Creates a connection to server and do login.

        Args:
            is_reconnect (bool, optional): If is reconnect. Defaults to False.
        """
        if is_reconnect and self.socket.open:
            await self.close()

        self.socket = None
        while self.socket is None:
            try:
                self.socket = await self._conn.__aenter__()
            except websockets.exceptions.InvalidStatusCode:
                log.error("Could not reach server websocket!")
                log.exception(traceback.format_exc())
                asyncio.sleep(1)
        
        await self._login()

    async def _login(self):
        log.info("Login..")
        while not await self.get_login_status():
            log.info("Waiting for login on server..")
            time.sleep(5)
        
        log.info("Node login was successful.")

    async def start(self):
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
        
        self.close()

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

        command = json.loads(message)

        if self.node_config.auth_hash and command.keys() and int(command.get(list(command.keys())[0], {}).get('status')) > 0:
            log.debug(command)
            return

        api_result = await ApiHandler().handle(command)

        log.debug(f"api_result: {api_result}")
        try:
            if api_result is not None:
                if 0 in api_result:
                    for key in api_result:
                        try:
                            self.send(
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
                self.node_config.update_config("node", "authhash", login_result['loginStatus']['data']['authhash'])
            except Exception:
                log.error(traceback.format_exc())
            log.debug(f"New auth_hash: {self.node_config.auth_hash}")

        elif login_status_code == 0:
            return True
        
        return False
