import logging
import requests
import urllib3
import json
import traceback
from requests.exceptions import ConnectionError, ReadTimeout

from typing import Union

from pathlib import Path


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
    
    def _send_request(self, url_path: str, data: dict = None) -> str:
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