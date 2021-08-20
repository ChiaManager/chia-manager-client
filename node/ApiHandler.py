import inspect
import logging
import os
import sys


from classes import UpdateNode
from node.ChiaHandler import ChiaHandler
from node.NodeHelper import NodeHelper
from node.NodeConfig import NodeConfig
from pathlib import Path

import websocket
from node.SystemInfo import SystemInfo

log = logging.getLogger()


class ApiHandler:
    config_object = {}

    def __init__(self, websocket: websocket.WebSocketApp):
        self.websocket = websocket
        self.node_config = NodeConfig()
        self.updateNode = UpdateNode()
        self.chiaInterpreter = ChiaHandler()
        self.systemInfoInterpreter = SystemInfo()

        self.request_map = {
            'loginStatus': None,
            'queryCronData': None,
            'updateNode': None,
            'nodeUpdateStatus': None,
            'acceptNodeRequest': None,
            'querySystemInfo': None,
            'queryWalletData': None,
            'queryFarmData': None,
            'queryHarvesterData': None,
            'queryWalletStatus': None,
            'queryFarmerStatus': None,
            'queryHarvesterStatus': None,
            'restartFarmerService': None,
            'restartWalletService': None,
            'restartHarvesterService': None
        }

    def interpretCommand(self, command):

        stack = inspect.stack()
        caller_class = stack[1][0].f_locals["self"].__class__.__name__
        caller_function = stack[1][0].f_code.co_name

        log.debug(f"function caller: {caller_class}.{caller_function}")
        log.debug(f"command: {command}")
        key = list(command.keys())[0]

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
                        0: NodeHelper().get_formated_info(auth_hash, "backendRequest", "ChiaMgmt\\Nodes\\Nodes_Api",
                                                               "Nodes_Api", "updateSystemInfo",
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
                elif key == "updateNode":
                    return self.updateNode.updateNode(command[key]["data"]["link"], command[key]["data"]["version"])
                elif key == "nodeUpdateStatus":
                    return NodeHelper().get_formated_info(auth_hash, "backendRequest", "ChiaMgmt\\Nodes\\Nodes_Api", "Nodes_Api", "nodeUpdateStatus", self.updateNode.getStatus())
                elif key == "acceptNodeRequest":
                    log.info(0, "Restarting node in background.")
                    execpath = "{}../chia_mgmt_node.py".format(Path(os.path.realpath(__file__)))
                    sys.exit(0)
                elif key == "querySystemInfo":
                    return NodeHelper().get_formated_info(auth_hash, "backendRequest", "ChiaMgmt\\Nodes\\Nodes_Api", "Nodes_Api", "updateSystemInfo", self.systemInfoInterpreter.get_system_info())
                elif key == "queryWalletData":
                    return NodeHelper().get_formated_info(auth_hash, "backendRequest", "ChiaMgmt\\Chia_Wallet\\Chia_Wallet_Api", "Chia_Wallet_Api", "updateWalletData", self.chiaInterpreter.get_wallet_info())
                elif key == "queryFarmData":
                    return NodeHelper().get_formated_info(auth_hash, "backendRequest", "ChiaMgmt\\Chia_Farm\\Chia_Farm_Api", "Chia_Farm_Api", "updateFarmData", self.chiaInterpreter.get_farmer_info())
                elif key == "queryHarvesterData":
                    return NodeHelper().get_formated_info(auth_hash, "backendRequest", "ChiaMgmt\\Chia_Harvester\\Chia_Harvester_Api", "Chia_Harvester_Api", "updateHarvesterData", self.chiaInterpreter.get_harvester_info())
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
            else:
                log.info(command[key]['message'])

        else:
            log.info(f"Command {command} not valid.")

    def send_login_status(self):
        self.websocket.send()
