from chia_api.ChiaApi import ChiaApi
from chia_api.ChiaDaemon import ChiaDaemon
from chia_api.constants import ServicesForGroup
from system.SystemInfo import IS_WINDOWS


class ChiaFarmerApi(ChiaApi):
    def __init__(self):
        super(ChiaFarmerApi, self).__init__()
        self.port = 8559
        self.service_name = "start_farmer.exe" if IS_WINDOWS else "chia_farmer"
    
    async def start(self, restart: bool = False):
        return await ChiaDaemon().start_service(service=ServicesForGroup.FARMER_ONLY, restart=restart)
                
    async def get_wallets(self):
        return self._send_request('get_wallets')
        
    async def get_signage_points(self):
        return self._send_request('get_signage_points').get('signage_points', {})

    async def get_transactions(self, wallet_id: int):
        return self._send_request('get_transactions', data={'wallet_id': wallet_id})
