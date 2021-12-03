
from chia_api.ChiaApi import ChiaApi, log


class ChiaHarvesterApi(ChiaApi):
    def __init__(self):
        super(ChiaHarvesterApi, self).__init__()
        self.port = 8560

    def get_plots(self):
        return self._send_request('get_plots').get('plots', {})

    def get_plot_directories(self):
        return self._send_request('get_plot_directories').get('directories', {})



        
