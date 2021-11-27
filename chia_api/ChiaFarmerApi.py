import logging
import json
from typing import Union
from pprint import pprint
from pathlib import Path

from chia_api.ChiaApi import ChiaApi, log

import requests


class ChiaFarmerApi(ChiaApi):
    def __init__(self):
        super(ChiaFarmerApi, self).__init__()
        self.port = 8559
                
    def get_wallets(self):
        return self._send_request('get_wallets')
        
    def get_signage_points(self):
        return self._send_request('get_signage_points')

    def get_transactions(self, wallet_id: int):
        return self._send_request('get_transactions', data={'wallet_id': wallet_id})
