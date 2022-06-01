import logging
import traceback
from typing import Union, Any

from node.ChiaHandler import ChiaHandler
from node.NodeConfig import NodeConfig
from system.SystemInfo import SystemInfo
from chia_api.ChiaDaemon import ChiaDaemon
from chia_api.ChiaWalletApi import ChiaWalletApi
from chia_api.ChiaFullNodeApi import ChiaFullNodeApi
from chia_api.ChiaHarvesterApi import ChiaHarvesterApi
from chia_api.ChiaFarmerApi import ChiaFarmerApi

log = logging.getLogger()


class ApiHandler:

    def __init__(self):
        self.node_config = NodeConfig()
        self.chia_handler = ChiaHandler()
        self.system_info = SystemInfo()

        self.chia_daemon = ChiaDaemon()
        self.full_node_api = ChiaFullNodeApi()
        self.chia_wallet_api = ChiaWalletApi()
        self.harvester_api = ChiaHarvesterApi()
        self.farmer_api = ChiaFarmerApi()

        self.request_map = {
            'loginStatus': self._login_status,
            'querySystemInfo': self._get_system_info,
            'queryWalletData': self._wallet_data,
            'queryFarmData': self._farmer_data,
            'queryHarvesterData': self._harvester_data,
            'get_chia_status': self._get_chia_status,
            'get_script_version' : self._get_script_version, 
            'queryWalletStatus': self._get_chia_status,
            'queryWalletTransactions': self._get_wallet_transactions,
            'restartFarmerService': self._restart_farmer_service,
            'restartWalletService': self._restart_wallet_service,
            'restart_chia_daemon': self._start_chia_daemon,
            'restartHarvesterService': self._restart_harvester_service,
        }

    async def handle(self, command: dict) -> Union[dict, None]:
        """Handle incomming socket commands.

        Args:
            command (dict): Parsed JSON command from Server.

        Returns:
            Union[dict, None]: Returns the requested data if requested command was found.
        """

        log.debug(f"command: {command}")
        # TODO: write command as value and not as key -> Server API change required
        key = list(command.keys())[0]
        log.debug(f"current_key: {key}")
        
        if command[key] is not None and "status" in command[key] and "message" in command[key]:
            log.debug(f"Got message from API on command {key}: {command[key]['message']}")

            if command[key]["status"] == 0:
                return await self.request_map[key]()
            else:
                log.info(command[key]['message'])
        else:
            log.info(f"Command {command} not valid.")

    @staticmethod
    def _formated_info(namespace: str, method: str, data: Any = [], action: str = "backendRequest") -> dict:
        return {
            "node": {
                'nodeinfo': {'hostname': NodeConfig().hostname},
                'socketaction': action
            },
            'request': {
                'data': data,
                'logindata': { 'authhash': NodeConfig().auth_hash },
                'backendInfo': { 'namespace': namespace, 'method': method }
            }
        }

    async def _get_system_info(self) -> dict:

        return self._formated_info(
            namespace="ChiaMgmt\\Chia_Infra_Sysinfo\\Chia_Infra_Sysinfo_Api",
            method="updateSystemInfo", 
            data=self.system_info.get_system_info(),
        )

    async def _login_status(self) -> dict:

        return self._formated_info(
            namespace="ChiaMgmt\\Nodes\\Nodes_Api", 
            method="updateScriptVersion",
            data={
                'scriptversion': self.node_config.get_script_info(),
                'chia': await self.chia_handler.get_chia_paths(),
            },
            action="ownRequest",
        )

    async def _get_chia_status(self) -> dict:

        return self._formated_info(
            namespace="ChiaMgmt\\Nodes\\Nodes_Api",
            method="updateChiaStatus", 
            data={
                'wallet': self.chia_wallet_api.get_status(),
                'farmer': self.farmer_api.get_status(),
                'harvester': self.harvester_api.get_status(),
                'daemon': self.chia_daemon.running(),
            }
        )
    
    async def _wallet_data(self) -> dict:
        log.info("Get wallet data..")
        data = {}

        if self.chia_wallet_api.get_status():
            # get wallet specific data from each wallet
            for wallet in self.chia_wallet_api.get_wallets().get('wallets', []):
                wallet_id = wallet['id']

                data[wallet_id] = {
                    'address': self.chia_wallet_api.get_next_address(wallet_id),
                    'height': self.chia_wallet_api.get_height_info(wallet_id),
                    'sync_status': self.chia_wallet_api.get_sync_status(wallet_id),
                    'type': wallet['type'],
                    'balance': self.chia_wallet_api.get_wallet_balance(wallet_id),
                }

            log.debug(f"data: {data}")
            log.info("Get wallet data.. Done!")
            
            
            return self._formated_info(
                namespace="ChiaMgmt\\Chia_Wallet\\Chia_Wallet_Api", 
                method="updateWalletData",
                data=data,
            )

    async def _get_wallet_transactions(self):
            log.debug("queryWalletTransactions")
            
            wallets = self.chia_wallet_api.get_wallets().get('wallets', None)

            if wallets is None:
                log.debug(f"No Wallets found!")
                return self._formated_info(
                    namespace="ChiaMgmt\\Chia_Wallet\\Chia_Wallet_Api",
                    method="updateWalletTransactions",
                    data={},
                )

            transactions = {}
            for wallet in wallets:
                transactions[wallet['id']] = self.chia_wallet_api.get_transactions(wallet['id'])

            log.debug(f"transactions: {transactions}")

            return self._formated_info(
                namespace="ChiaMgmt\\Chia_Wallet\\Chia_Wallet_Api",
                method="updateWalletTransactions", 
                data=transactions,
            )

    async def _farmer_data(self) -> dict:
        if self.farmer_api.get_status():
            farmed_amount = {}
        
            for wallet in self.chia_wallet_api.get_wallets().get('wallets', []):
                for key, value in self.chia_wallet_api.get_farmed_amount(wallet['id']).items():
                    farmed_amount[key] = farmed_amount[key] + value if farmed_amount.get(key) is not None else value

            data = farmed_amount

            # get plot count and size
            plots = await self.harvester_api.get_plots()
            if 'plots' in plots: plots = plots.get('plots', [])


            farmer = {
                'signage_points': await self.farmer_api.get_signage_points(), # challenges
                'total_size_of_plots': sum(map(lambda x: x["file_size"], plots)),
                'plot_count': len(plots),
            }

            # get farming status and estimated network space
            blockchain_state = await self.full_node_api.get_blockchain_state()
            farmer['farming_status'] = blockchain_state.get('sync')
            farmer['estimated_network_space'] = blockchain_state.get('space')

            # calculate expected time to win 
            average_block_time = (24 * 3600) / 4608 # SECONDS_PER_BLOCK
            blocks_to_compare = 500

            if blockchain_state.get("peak"):
                try:
                    curr_block = blockchain_state["peak"]
                    if curr_block is not None and curr_block['height'] > 0 and not curr_block.get('timestamp') is not None:
                        curr_block = await self.full_node_api.get_block_record(curr_block['prev_hash'])

                    if curr_block is not None:
                        # get the block from the past for calculation (curr block - 500)
                        past_block = await self.full_node_api.get_block_record_by_height(curr_block['height'] - blocks_to_compare)
                        if past_block is not None and past_block['height'] > 0 and not past_block.get('timestamp') is not None:
                            past_block = await self.full_node_api.get_block_record(past_block['prev_hash'])

                        average_block_time = (curr_block['timestamp'] - past_block['timestamp']) / (curr_block['height'] - past_block['height'])
                except (TypeError, KeyError):
                    log.debug(traceback.format_exc())

            proportion = farmer['total_size_of_plots'] / farmer['estimated_network_space'] if farmer['estimated_network_space'] else -1
            minutes = int((average_block_time / 60) / proportion) if proportion else -1

            farmer['expected_time_to_win'] = minutes

            data.update(farmer)

            return self._formated_info(
                namespace="ChiaMgmt\\Chia_Farm\\Chia_Farm_Api",
                method="updateFarmData",
                data=data
            )

    async def _harvester_data(self) -> dict:
        if self.harvester_api.get_status():
            plot_directories = await self.harvester_api.get_plot_directories()
            plots = await self.harvester_api.get_plots()

            data = {plot_path:[] for plot_path in plot_directories}

            for plot in plots:
                for plot_path in plot_directories:
                    if plot['filename'].startswith(plot_path):
                        data[plot_path].append(plot)

            return self._formated_info(
                namespace="ChiaMgmt\\Chia_Harvester\\Chia_Harvester_Api",
                method="updateHarvesterData",
                data=data
            )

    async def _get_script_version(self) -> dict:
        data = {}
        data["scriptversion"] = self.node_config.get_script_info()
        data["chia"] = await self.chia_handler.get_chia_paths()
        
        return self._formated_info(
            namespace="ChiaMgmt\\Nodes\\Nodes_Api",
            method="updateScriptVersion",
            data=data
        )

    async def _restart_farmer_service(self):
        return self._formated_info(
            namespace="ChiaMgmt\\Chia_Farm\\Chia_Farm_Api",
            method="farmerServiceRestart",
            data=self.farmer_api.start(restart=True)
        )   

    async def _restart_wallet_service(self):
        return self._formated_info(
            namespace="ChiaMgmt\\Chia_Wallet\\Chia_Wallet_Api",
            method="walletServiceRestart", 
            data=await self.chia_wallet_api.start(restart=True)
        )

    async def _restart_harvester_service(self):
        return self._formated_info(
            namespace="ChiaMgmt\\Chia_Harvester\\Chia_Harvester_Api",
            method="harvesterServiceRestart", 
            data=self.harvester_api.start(restart=True)
        )

    async def _start_chia_daemon(self):
        return self._formated_info(
            namespace="ChiaMgmt\\Chia_Harvester\\Chia_Daemon_Api",
            method="harvesterServiceRestart", 
            data=self.chia_daemon.start()
        )