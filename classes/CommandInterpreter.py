from .ChiaConfigParser import ChiaConfigParser
from .RequestBuilder import RequestBuilder
from .UpdateNode import UpdateNode
from .ChiaInterpreter import ChiaInterpreter
from .SystemInfoInterpreter import SystemInfoInterpreter
from pathlib import Path

import sys

class CommandInterpreter:
    config_object = {}

    def __init__(self, consoleFileOutputWriter):
        self.consoleFileOutputWriter = consoleFileOutputWriter
        self.chiaConfigParser = ChiaConfigParser()
        self.requestBuilder = RequestBuilder()
        self.updateNode = UpdateNode()
        self.chiaInterpreter = ChiaInterpreter()
        self.systemInfoInterpreter = SystemInfoInterpreter()

    def interpretCommand(self, command):
        key = list(command.keys())[0]

        if command[key] is not None and "status" in command[key] and "message" in command[key]:
            self.consoleFileOutputWriter.writeToConsoleAndFile(0, "Got message from API on command {}: {}".format(key, command[key]["message"]))

            if command[key]["status"] == 0:
                if key == "loginStatus":
                    self.consoleFileOutputWriter.writeToConsoleAndFile(0, "This node is logged in. Nodeinformation: Node hostname: {} Registered as: {}".format(command[key]["data"]["hostname"], command[key]["data"]["nodetype"]))
                    datatosend = {}
                    datatosend["scriptversion"] = self.chiaConfigParser.get_script_info()
                    datatosend["chia"] = self.chiaInterpreter.getChiaVersionAndInstallPath()
                    return self.requestBuilder.getFormatedInfo(self.chiaConfigParser.get_node_info()["authhash"], "ownRequest", "ChiaMgmt\\Nodes\\Nodes_Api", "Nodes_Api", "updateScriptVersion", datatosend);
                elif key == "queryCronData":
                    command = {}
                    command[0] = self.requestBuilder.getFormatedInfo(self.chiaConfigParser.get_node_info()["authhash"], "backendRequest", "ChiaMgmt\\Nodes\\Nodes_Api", "Nodes_Api", "updateSystemInfo", self.systemInfoInterpreter.querySystemData())
                    command[1] = self.requestBuilder.getFormatedInfo(self.chiaConfigParser.get_node_info()["authhash"], "backendRequest", "ChiaMgmt\\Chia_Wallet\\Chia_Wallet_Api", "Chia_Wallet_Api", "updateWalletData", self.chiaInterpreter.getWalletInformations())
                    command[2] = self.requestBuilder.getFormatedInfo(self.chiaConfigParser.get_node_info()["authhash"], "backendRequest", "ChiaMgmt\\Chia_Farm\\Chia_Farm_Api", "Chia_Farm_Api", "updateFarmData", self.chiaInterpreter.getFarmerInformations())
                    command[3] = self.requestBuilder.getFormatedInfo(self.chiaConfigParser.get_node_info()["authhash"], "backendRequest", "ChiaMgmt\\Chia_Wallet\\Chia_Wallet_Api", "Chia_Wallet_Api", "walletStatus", self.chiaInterpreter.checkWalletRunning("json"))
                    command[4] = self.requestBuilder.getFormatedInfo(self.chiaConfigParser.get_node_info()["authhash"], "backendRequest", "ChiaMgmt\\Chia_Farm\\Chia_Farm_Api", "Chia_Farm_Api", "farmerStatus", self.chiaInterpreter.checkFarmerRunning("json"))
                    return command;
                elif key == "updateNode":
                    return self.updateNode.updateNode(command[key]["data"]["link"], command[key]["data"]["version"])
                elif key == "nodeUpdateStatus":
                    return self.requestBuilder.getFormatedInfo(self.chiaConfigParser.get_node_info()["authhash"], "backendRequest", "ChiaMgmt\\Nodes\\Nodes_Api", "Nodes_Api", "nodeUpdateStatus", self.updateNode.getStatus());
                elif key == "acceptNodeRequest":
                    self.consoleFileOutputWriter.writeToConsoleAndFile(0, "Restarting client in background.")
                    execpath = "{}../chia_mgmt_node.py".format(Path(os.path.realpath(__file__)))
                    sys.exit()
                elif key == "querySystemInfo":
                    return self.requestBuilder.getFormatedInfo(self.chiaConfigParser.get_node_info()["authhash"], "backendRequest", "ChiaMgmt\\Nodes\\Nodes_Api", "Nodes_Api", "updateSystemInfo", self.systemInfoInterpreter.querySystemData())
                elif key == "queryWalletData":
                    return self.requestBuilder.getFormatedInfo(self.chiaConfigParser.get_node_info()["authhash"], "backendRequest", "ChiaMgmt\\Chia_Wallet\\Chia_Wallet_Api", "Chia_Wallet_Api", "updateWalletData", self.chiaInterpreter.getWalletInformations());
                elif key == "queryFarmData":
                    return self.requestBuilder.getFormatedInfo(self.chiaConfigParser.get_node_info()["authhash"], "backendRequest", "ChiaMgmt\\Chia_Farm\\Chia_Farm_Api", "Chia_Farm_Api", "updateFarmData", self.chiaInterpreter.getFarmerInformations());
                elif key == "queryWalletStatus":
                    return self.requestBuilder.getFormatedInfo(self.chiaConfigParser.get_node_info()["authhash"], "backendRequest", "ChiaMgmt\\Chia_Wallet\\Chia_Wallet_Api", "Chia_Wallet_Api", "walletStatus", self.chiaInterpreter.checkWalletRunning("json"))
                elif key == "queryFarmerStatus":
                    return self.requestBuilder.getFormatedInfo(self.chiaConfigParser.get_node_info()["authhash"], "backendRequest", "ChiaMgmt\\Chia_Farm\\Chia_Farm_Api", "Chia_Farm_Api", "farmerStatus", self.chiaInterpreter.checkFarmerRunning("json"));
                elif key == "restartFarmerService":
                    return self.requestBuilder.getFormatedInfo(self.chiaConfigParser.get_node_info()["authhash"], "backendRequest", "ChiaMgmt\\Chia_Farm\\Chia_Farm_Api", "Chia_Farm_Api", "farmerServiceRestart", self.chiaInterpreter.farmerServiceRestart());
                elif key == "restartWalletService":
                    return self.requestBuilder.getFormatedInfo(self.chiaConfigParser.get_node_info()["authhash"], "backendRequest", "ChiaMgmt\\Chia_Wallet\\Chia_Wallet_Api", "Chia_Wallet_Api", "walletServiceRestart", self.chiaInterpreter.walletServiceRestart());
            else:
                self.consoleFileOutputWriter.writeToConsoleAndFile(1, "{}".format(command[key]["message"]))

        else:
            self.consoleFileOutputWriter.writeToConsoleAndFile(1, "Command {} not valid.".format(command))
