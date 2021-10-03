import logging
import requests
import urllib3
import json

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
    
    def _send_request(self, port: int, url_path: str, data: Union[dict] = None) -> str:
        url = f"https://localhost:{port}/{url_path}"
        response = requests.post(
            url, 
            json=data or {},
            headers={'content-type': 'application/json'}, 
            cert=self.cert, 
            verify=False
        ) 
        
        result = json.loads(response.text)
        
        del result['success']
        print(f"result: {result}")
        return result