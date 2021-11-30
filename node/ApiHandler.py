import os
import sys
import logging
from pathlib import Path

from node.ChiaHandler import ChiaHandler
from node.NodeHelper import NodeHelper
from node.NodeConfig import NodeConfig
from system.SystemInfo import SystemInfo
from chia_api.ChiaWalletApi import ChiaWalletApi
from chia_api.ChiaFullNodeApi import ChiaFullNodeApi
from chia_api.ChiaHarvesterApi import ChiaHarvesterApi
from chia_api.ChiaFarmerApi import ChiaFarmerApi

import websocket


log = logging.getLogger()


class ApiHandler:
    config_object = {}

    def __init__(self, websocket: websocket.WebSocketApp):
        self.websocket = websocket
        self.node_config = NodeConfig()
        self.chiaInterpreter = ChiaHandler()
        self.systemInfoInterpreter = SystemInfo()

        self.full_node_api = ChiaFullNodeApi()
        self.chia_wallet_api = ChiaWalletApi()
        self.harvester_api = ChiaHarvesterApi()
        self.farmer_api = ChiaFarmerApi()

        self.request_map = {
            'loginStatus': None,
            'queryCronData': None,
            'nodeUpdateStatus': None,
            'acceptNodeRequest': None,
            'querySystemInfo': None,
            'queryWalletData': self._wallet_data,
            'queryFarmData': self._farmer_data,
            'queryHarvesterData': None,
            'queryWalletStatus': None,
            'queryFarmerStatus': None,
            'queryHarvesterStatus': None,
            'restartFarmerService': None,
            'restartWalletService': None,
            'restartHarvesterService': None
        }

    def interpretCommand(self, command):

        log.debug(f"command: {command}")
        key = list(command.keys())[0]
        log.debug(f"current_key: {key}")
        
        if command[key] is not None and "status" in command[key] and "message" in command[key]:
            log.debug(f"Got message from API on command {key}: {command[key]['message']}")

            if command[key]["status"] == 0:
                auth_hash = self.node_config.auth_hash
                if key == "loginStatus":
                    log.info("This node is logged in. Nodeinformation: Node hostname: {} Registered as: {}".format(command[key]["data"]["hostname"], command[key]["data"]["nodetype"]))
                    data = {
                        'scriptversion': self.node_config.get_script_info(),
                        'chia': self.chiaInterpreter.get_chia_paths()
                    }
                    return NodeHelper().get_formated_info(auth_hash, "ownRequest", "ChiaMgmt\\Nodes\\Nodes_Api", "Nodes_Api", "updateScriptVersion", data)
                elif key == "queryCronData":
                    log.debug("in queryCronData")
                    command = {
                        0: NodeHelper().get_formated_info(auth_hash, "backendRequest", "ChiaMgmt\\Chia_Infra_Sysinfo\\Chia_Infra_Sysinfo_Api",
                                                               "Chia_Infra_Sysinfo_Api", "updateSystemInfo",
                                                               self.systemInfoInterpreter.get_system_info()),
                        1: NodeHelper().get_formated_info(auth_hash, "backendRequest",
                                                               "ChiaMgmt\\Chia_Wallet\\Chia_Wallet_Api",
                                                               "Chia_Wallet_Api", "updateWalletData",
                                                               self.chiaInterpreter.get_wallet_info()),
                        2: NodeHelper().get_formated_info(auth_hash, "backendRequest",
                                                               "ChiaMgmt\\Chia_Farm\\Chia_Farm_Api", "Chia_Farm_Api",
                                                               "updateFarmData",
                                                               self.chiaInterpreter.get_farmer_info()),
                        3: NodeHelper().get_formated_info(auth_hash, "backendRequest",
                                                               "ChiaMgmt\\Chia_Harvester\\Chia_Harvester_Api",
                                                               "Chia_Harvester_Api", "updateHarvesterData",
                                                               self.chiaInterpreter.get_harvester_info()),
                        4: NodeHelper().get_formated_info(auth_hash, "backendRequest",
                                                               "ChiaMgmt\\Chia_Wallet\\Chia_Wallet_Api",
                                                               "Chia_Wallet_Api", "walletStatus",
                                                               self.chiaInterpreter.get_wallet_status(
                                                                   as_dict=True)),
                        5: NodeHelper().get_formated_info(auth_hash, "backendRequest",
                                                               "ChiaMgmt\\Chia_Farm\\Chia_Farm_Api", "Chia_Farm_Api",
                                                               "farmerStatus",
                                                               self.chiaInterpreter.get_farmer_status(True)),
                        6: NodeHelper().get_formated_info(auth_hash, "backendRequest",
                                                               "ChiaMgmt\\Chia_Harvester\\Chia_Harvester_Api",
                                                               "Chia_Harvester_Api", "harvesterStatus",
                                                               self.chiaInterpreter.get_harvester_status(True))}
                    return command
                elif key == "acceptNodeRequest":
                    log.info(0, "Restarting node in background.")
                    execpath = "{}../chia_mgmt_node.py".format(Path(os.path.realpath(__file__)))
                    sys.exit(0)
                elif key == "querySystemInfo":
                    return NodeHelper().get_formated_info(auth_hash, "backendRequest", "ChiaMgmt\\Chia_Infra_Sysinfo\\Chia_Infra_Sysinfo_Api", "Chia_Infra_Sysinfo_Api", "updateSystemInfo", self.systemInfoInterpreter.get_system_info())
                elif key == "queryWalletData":
                    return self.request_map[key]()
                elif key == "queryFarmData":
                    return self.request_map[key]()
                elif key == "queryWalletStatus":
                    return NodeHelper().get_formated_info(auth_hash, "backendRequest", "ChiaMgmt\\Chia_Wallet\\Chia_Wallet_Api", "Chia_Wallet_Api", "walletStatus", self.chiaInterpreter.get_wallet_status(True))
                elif key == "queryFarmerStatus":
                    return NodeHelper().get_formated_info(auth_hash, "backendRequest", "ChiaMgmt\\Chia_Farm\\Chia_Farm_Api", "Chia_Farm_Api", "farmerStatus", self.chiaInterpreter.get_farmer_status(True))
                elif key == "queryHarvesterStatus":
                    return NodeHelper().get_formated_info(auth_hash, "backendRequest", "ChiaMgmt\\Chia_Harvester\\Chia_Harvester_Api", "Chia_Harvester_Api", "harvesterStatus", self.chiaInterpreter.get_harvester_status(True))
                elif key == "restartFarmerService":
                    return NodeHelper().get_formated_info(auth_hash, "backendRequest", "ChiaMgmt\\Chia_Farm\\Chia_Farm_Api", "Chia_Farm_Api", "farmerServiceRestart", self.chiaInterpreter.restart_farmer())
                elif key == "restartWalletService":
                    return NodeHelper().get_formated_info(auth_hash, "backendRequest", "ChiaMgmt\\Chia_Wallet\\Chia_Wallet_Api", "Chia_Wallet_Api", "walletServiceRestart", self.chiaInterpreter.restart_wallet())
                elif key == "restartHarvesterService":
                    return NodeHelper().get_formated_info(auth_hash, "backendRequest", "ChiaMgmt\\Chia_Harvester\\Chia_Harvester_Api", "Chia_Harvester_Api", "harvesterServiceRestart", self.chiaInterpreter.restart_harvester())
                elif key == "queryWalletTransactions":
                    log.debug("queryWalletTransactions")
                    
                    wallets = self.chia_wallet_api.get_wallets().get('wallets', None)

                    if wallets is None:
                        log.debug(f"No Wallets found!")
                        return NodeHelper().get_formated_info(auth_hash, "backendRequest", "ChiaMgmt\\Chia_Wallet\\Chia_Wallet_Api", "Chia_Wallet_Api", "updateWalletTransactions", [])

                    transactions = {}
                    for wallet in wallets:
                        transactions[wallet['id']] = self.chia_wallet_api.get_transactions(wallet['id'])

                    log.debug(f"transactions: {transactions}")
                    return NodeHelper().get_formated_info(auth_hash, "backendRequest", "ChiaMgmt\\Chia_Wallet\\Chia_Wallet_Api", "Chia_Wallet_Api", "updateWalletTransactions", transactions)


            else:
                log.info(command[key]['message'])

        else:
            log.info(f"Command {command} not valid.")

    def _wallet_data(self) -> dict:
        log.info("Get wallet data..")
        data = {}
    
        # get wallet specific data from each wallet
        for wallet in self.chia_wallet_api.get_wallets().get('wallets', []):
            wallet_id = wallet['id']

            data[wallet_id] = {
                'address': self.chia_wallet_api.get_next_address(wallet_id),
                'height': self.chia_wallet_api.get_height_info(wallet_id),
                'sync_status': self.chia_wallet_api.get_sync_status(wallet_id),
                'type': wallet['type'],
                'balance': self.chia_wallet_api.get_wallet_balance(wallet_id)
            }

        log.debug(f"data: {data}")
        log.info("Get wallet data.. Done!")
        
        return NodeHelper().get_formated_info(self.node_config.auth_hash, "backendRequest", "ChiaMgmt\\Chia_Wallet\\Chia_Wallet_Api", "Chia_Wallet_Api", "updateWalletData", data)

    def _farmer_data(self) -> dict:
        data = {'wallets': {}}
      
        for wallet in self.chia_wallet_api.get_wallets().get('wallets', []):
            wallet_id = wallet['id']

            data['wallets'][wallet_id] = {
                "farmed_amount": self.chia_wallet_api.get_farmed_amount(wallet_id),
                "signage_points": self.farmer_api.get_signage_points() # challenges
            }
        # get plot count and size
        plots = self.harvester_api.get_plots().get('plots', [])

        farmer = {}
        farmer['total_size_of_plots'] = sum(map(lambda x: x["file_size"], plots))
        farmer['plot_count'] = len(plots)

        # get farming status and estimated network space
        blockchain_state = self.full_node_api.get_blockchain_state()
        farmer['farming_status'] = blockchain_state.get('blockchain_state', {}).get('sync')
        farmer['estimated_network_space'] = blockchain_state.get('blockchain_state', {}).get('space')

        # calculate expected time to win 
        average_block_time = (24 * 3600) / 4608 # SECONDS_PER_BLOCK
        blocks_to_compare = 500

        try:
            curr_block = blockchain_state["peak"]
            if curr_block is not None and curr_block['height'] > 0 and not curr_block.get('timestamp') is not None:
                curr_block = self.full_node_api.get_block_record(curr_block['prev_hash'])

            if curr_block is not None:
                # get the block from the past for calculation (curr block - 500)
                past_block = self.full_node_api.get_block_record_by_height(curr_block['height'] - blocks_to_compare)
                if past_block is not None and past_block['height'] > 0 and not past_block.get('timestamp') is not None:
                    past_block = self.full_node_api.get_block_record(past_block['prev_hash'])

                average_block_time = (curr_block['timestamp'] - past_block['timestamp']) / (curr_block['height'] - past_block['height'])
        except (TypeError, KeyError):
            pass

        proportion = farmer['total_size_of_plots'] / farmer['estimated_network_space'] if farmer['estimated_network_space'] else -1
        minutes = int((average_block_time / 60) / proportion) if proportion else -1

        farmer['expected_time_to_win'] = minutes

        data['farmer'] = farmer

        return NodeHelper().get_formated_info(self.node_config.auth_hash, "backendRequest", "ChiaMgmt\\Chia_Farm\\Chia_Farm_Api", "Chia_Farm_Api", "updateFarmData", data)

