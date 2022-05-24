from chia_api.ChiaApi import ChiaApi, log
from chia_api.ChiaDaemon import ChiaDaemon
from chia_api.constants import ServicesForGroup


class ChiaHarvesterApi(ChiaApi):
    def __init__(self):
        super(ChiaHarvesterApi, self).__init__()
        self.service_name = "chia_harvester"
        self.port = 8560

    async def start(self, restart: bool = False):
        return await ChiaDaemon().start_service(service=ServicesForGroup.HARVESTER, restart=restart)

    async def get_plots(self) -> dict:
        return self._send_request('get_plots').get('plots', {})

    async def get_plot_directories(self) -> dict:
        return self._send_request('get_plot_directories').get('directories', {})
