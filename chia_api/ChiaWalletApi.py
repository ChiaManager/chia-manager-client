import logging
import urllib3
import json
from typing import Union
from pprint import pprint
from pathlib import Path

from chia_api.ChiaApi import ChiaApi

import requests

log = logging.getLogger()
# chia certificates can't be validated because they are self signed by default
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class ChiaWalletApi(ChiaApi):
    def __init__(self):
        super(ChiaWalletApi, self).__init__()
        # todo: read ports from ~/.chia/mainnet/config/config.yaml
        self.port = 9256
        
    def __send_wallet_request(self, url_path: str, data: Union[dict] = None):
        return self._send_request(self.port, url_path=url_path, data=data)
        
    def get_wallets(self):
        return self.__send_wallet_request('get_wallets')

    def get_transactions(self, wallet_id: int):
        log.debug(f"get_transactions for wallet_id {wallet_id}")
        return self.__send_wallet_request('get_transactions', data={'wallet_id': wallet_id})