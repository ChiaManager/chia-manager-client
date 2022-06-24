import logging
import requests
import urllib3
import json
import traceback
from typing import Union
from pathlib import Path

import psutil
from requests.exceptions import ConnectionError, ReadTimeout

from node.NodeConfig import NodeConfig


log = logging.getLogger()
# chia certificates can't be validated because they are self signed
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class ChiaApi:
    def __init__(self):
        self.cert = (
            f"{Path.home()}/.chia/mainnet/config/ssl/full_node/private_full_node.crt", 
            f"{Path.home()}/.chia/mainnet/config/ssl/full_node/private_full_node.key"
            )
        
        self.port = None
        self.service_name = None

    def _send_request(self, url_path: str, data: Union[dict, None] = None) -> dict:
        if self.port is None:
            raise Exception("Port is missing. Please specify a Port.")
            
        url = f"https://localhost:{self.port}/{url_path}"
        log.debug(f"Send request to : {url}")
        try:
            response = requests.post(
                url, 
                json=data or {},
                headers={'content-type': 'application/json'}, 
                cert=self.cert, 
                verify=False,
                timeout=15,
            ) 
        except (ConnectionError, ReadTimeout):
            log.info(f"Could not connect to {url}")
            return {}
        except Exception:
            print(traceback.format_exc())
            return {}

        try:
            result = json.loads(response.text)
        except Exception:
            log.exception(traceback.format_exc())
            return {}

        if result.get('success', False):
            del result['success']
        else:
            log.exception(result)
            result = {}

        return result

    def get_status(self) -> bool:
        if self.service_name is None:
            return False

        ## Winodoof
        # Chia.exe = GUI
        # daemon.exe
        # start_farmer.exe
        # start_full_node.exe
        # start_harvester.exe
        # start_wallet.exe

        # currently not supported:
        # start_introducer.exe
        # start_timelord.exe
        return self.service_name in [p.name()for p in psutil.process_iter()]
