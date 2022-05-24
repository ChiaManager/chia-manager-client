import logging
import json
from typing import Union
from pprint import pprint
from pathlib import Path

from chia_api.ChiaApi import ChiaApi, log

import requests

from chia_api.ChiaDaemon import ChiaDaemon
from chia_api.constants import ServicesForGroup


class ChiaWalletApi(ChiaApi):
    def __init__(self):
        super(ChiaWalletApi, self).__init__()
        # TODO: read ports from ~/.chia/mainnet/config/config.yaml
        self.port = 9256
        self.service_name = "chia_wallet"
    
    async def start(self, restart: bool = False):
        return await ChiaDaemon().start_service(service=ServicesForGroup.WALLET_ONLY, restart=restart)    

    def get_wallets(self):
        return self._send_request('get_wallets')

    def get_farmed_amount(self, wallet_id: int):
        return self._send_request('get_farmed_amount', data={'wallet_id': wallet_id})

    def get_transactions(self, wallet_id: int):
        return self._send_request('get_transactions', data={'wallet_id': wallet_id})

    def get_height_info(self, wallet_id: int):
        # get sync height
        return self._send_request('get_height_info', data={'wallet_id': wallet_id}).get('height')

    def get_wallet_balance(self, wallet_id: int):
        return self._send_request('get_wallet_balance', data={'wallet_id': wallet_id}).get('wallet_balance')

    def get_next_address (self, wallet_id: int):
        # get current wallet adress
        return self._send_request(
            'get_next_address', 
            data={'wallet_id': wallet_id, 'new_address': False}
        ).get('address')

    def get_sync_status (self, wallet_id: int):
        return self._send_request('get_sync_status', data={'wallet_id': wallet_id})