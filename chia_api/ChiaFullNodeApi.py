from chia_api.ChiaApi import ChiaApi, log

class ChiaFullNodeApi(ChiaApi):
    def __init__(self):
        super(ChiaFullNodeApi, self).__init__()
        self.port = 8555

    def get_plots(self):
        return self._send_request('get_plots')

    def get_blockchain_state(self):
        return self._send_request('get_blockchain_state').get('blockchain_state', {})
        
    def get_block_record_by_height(self, wallet_height):
        return self._send_request('get_block_record_by_height', data={'height': wallet_height})
        
    def get_block_record(self, header_hash: str) -> dict:
        # get header_hash from get_block_record_by_height 
        return self._send_request('get_block_record', data={'header_hash': header_hash})