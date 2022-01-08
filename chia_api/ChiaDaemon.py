import ssl
import asyncio
import websockets
import logging
import traceback
import json
from pathlib import Path, PosixPath
from typing import Union
from secrets import token_bytes

from chia_api.helper import dict_to_json_str
from chia_api.constants import ServicesForGroup

log = logging.getLogger()

class ChiaDaemon():
    def __init__(self) -> None:
        # TODO: read cert paths and daemon port from chia config.yml
        self.daemon_wss_port = 55400
        self.daemon_wss_url = f"wss://127.0.0.1:{self.daemon_wss_port}"
        self.ssl_context = self._ssl_context_for_client(
            ca_cert=Path.home().joinpath(".chia/mainnet/config/ssl/ca/private_ca.crt"),
            private_cert_path=Path.home().joinpath(".chia/mainnet/config/ssl/daemon/private_daemon.crt"),
            private_key_path=Path.home().joinpath(".chia/mainnet/config/ssl/daemon/private_daemon.key"),
        )

    @classmethod
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(ChiaDaemon, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

    def _ssl_context_for_client(self, ca_cert: PosixPath, private_cert_path: PosixPath, private_key_path: PosixPath) -> ssl.SSLContext:
        # source: https://github.com/Chia-Network/chia-blockchain/blob/main/chia/server/server.py#L65

        ssl_context = ssl._create_unverified_context(purpose=ssl.Purpose.SERVER_AUTH, cafile=str(ca_cert))
        ssl_context.check_hostname = False
        ssl_context.load_cert_chain(certfile=str(private_cert_path), keyfile=str(private_key_path))
        ssl_context.verify_mode = ssl.CERT_REQUIRED
        return ssl_context

    async def _send(self, command: dict, data: dict = None, ack: bool = True) -> dict:

        command = {
                'command': command,
                'ack': ack,
                'data': data or '',
                'request_id': token_bytes().hex(),
                'destination': 'daemon',
                'origin': 'client',
        }

        log.debug(f"command: {command}")
        res = {}

        try:
            async with websockets.connect(self.daemon_wss_url, max_size=None, ssl=self.ssl_context, close_timeout=30) as websocket:
                await websocket.send(dict_to_json_str(command))
                data = await asyncio.wait_for(websocket.recv(), timeout=10)
                res = json.loads(data)
        except asyncio.exceptions.TimeoutError:
            log.error("Couldn't load data from Chia daemon (Timedout). Is the process running?")
        except Exception:
            log.exception(traceback.format_exc())

        
        log.debug(res)
        return res

    def get_chia_version(self) -> Union[str, None]:

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        res = loop.run_until_complete(
            self._send(command='get_version')
        )
        
        return res.get('data', {}).get('version') or None

    def start_service(self, service: ServicesForGroup, restart: bool = False) -> dict:
        # TODO: remove duplicate code
        restart = True
        if restart:
            loop = asyncio.get_event_loop()

            log.info(f"check is_running: {service.name}")
            res = loop.run_until_complete(
                self._send(
                    command='stop_service',
                    data={"service": service.value},
                    ack=False,
                )
            )

            log.debug(res)

        log.info(f"Start chia service: {service.name}")

        res = loop.run_until_complete(
            self._send(
                command='start_service',
                data={"service": service.value},
            )
        )
        
        res = res.get('data', {})
        if not res.get('success'):
            return {'success': False, 'error': res.get('error')}

        return {'success': True, 'error': None}

