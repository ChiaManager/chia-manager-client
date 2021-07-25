from .ChiaConfigParser import ChiaConfigParser
from .RequestBuilder import RequestBuilder
from .UpdateNode import UpdateNode
from .ChiaInterpreter import ChiaInterpreter
from pathlib import Path

import subprocess, os, sys

class CommandInterpreter:
    config_object = {}

    def __init__(self, consoleFileOutputWriter):
        self.consoleFileOutputWriter = consoleFileOutputWriter
        self.chiaConfigParser = ChiaConfigParser()
        self.requestBuilder = RequestBuilder()
        self.updateNode = UpdateNode()
        self.chiaInterpreter = ChiaInterpreter()

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
                    command[0] = self.requestBuilder.getFormatedInfo(self.chiaConfigParser.get_node_info()["authhash"], "backendRequest", "ChiaMgmt\\Nodes\\Nodes_Api", "Nodes_Api", "updateSystemInfo", self.querySystemData());
                    command[1] = self.requestBuilder.getFormatedInfo(self.chiaConfigParser.get_node_info()["authhash"], "backendRequest", "ChiaMgmt\\Chia_Wallet\\Chia_Wallet_Api", "Chia_Wallet_Api", "updateWalletData", self.chiaInterpreter.getWalletInformations());
                    command[2] = self.requestBuilder.getFormatedInfo(self.chiaConfigParser.get_node_info()["authhash"], "backendRequest", "ChiaMgmt\\Chia_Farm\\Chia_Farm_Api", "Chia_Farm_Api", "updateFarmData", self.chiaInterpreter.getFarmerInformations());
                    command[3] = self.requestBuilder.getFormatedInfo(self.chiaConfigParser.get_node_info()["authhash"], "backendRequest", "ChiaMgmt\\Chia_Wallet\\Chia_Wallet_Api", "Chia_Wallet_Api", "walletStatus", self.chiaInterpreter.checkWalletRunning("json"))
                    command[4] = self.requestBuilder.getFormatedInfo(self.chiaConfigParser.get_node_info()["authhash"], "backendRequest", "ChiaMgmt\\Chia_Farm\\Chia_Farm_Api", "Chia_Farm_Api", "farmerStatus", self.chiaInterpreter.checkFarmerRunning("json"));
                    return command;
                elif key == "updateNode":
                    return self.updateNode.updateNode(command[key]["data"]["link"], command[key]["data"]["version"])
                elif key == "nodeUpdateStatus":
                    return self.requestBuilder.getFormatedInfo(self.chiaConfigParser.get_node_info()["authhash"], "backendRequest", "ChiaMgmt\\Nodes\\Nodes_Api", "Nodes_Api", "nodeUpdateStatus", self.updateNode.getStatus());
                elif key == "acceptNodeRequest":
                    self.consoleFileOutputWriter.writeToConsoleAndFile(0, "Restarting client in background.")
                    execpath = "{}../chia_mgmt_node.py".format(Path(os.path.realpath(__file__)))
                    sys.exit()
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

    def querySystemData(self):
        data = {}
        data["system"] = {}
        data["system"]["load"] = self.calcLoadAvg()
        data["system"]["memory"] = self.getMemory()
        data["system"]["swap"] = self.getSwap()
        data["system"]["filesystem"] = self.getFilesystems()
        data["system"]["cpu"] = self.getCPU()

        return data

    def calcLoadAvg(self):
        returndata = {}
        loadavg = subprocess.getoutput("cat /proc/loadavg")
        returndata["1min"] = loadavg.split(" ")[0]
        returndata["5min"] = loadavg.split(" ")[1]
        returndata["15min"] = loadavg.split(" ")[2]
        return returndata;

    def getFilesystems(self):
        filesystems = subprocess.getoutput("df -h | tail -n +2").splitlines()
        returndata = []

        for filesystem in filesystems:
            filesystemplitted = filesystem.split(" ")
            thisfilesystem = []
            for thissplit in filesystemplitted:
                if thissplit != "":
                    thisfilesystem.append(thissplit)

            returndata.append(thisfilesystem)

        return returndata

    def getMemory(self):
        returndata = {}
        memoryinfo = subprocess.getoutput("cat /proc/meminfo | egrep 'MemTotal:|\MemFree:|\Buffers:|\Cached:|\SReclaimable:|\Shmem:' | awk '{print $2}'").splitlines()
        returndata["total"] = memoryinfo[0]
        returndata["free"] = memoryinfo[1]
        returndata["buffers"] = memoryinfo[2]
        returndata["cached"] = memoryinfo[3]
        returndata["shmem"] = memoryinfo[5]
        returndata["sreclaimable"] = memoryinfo[7]

        return returndata

    def getSwap(self):
        returndata = {}
        swapinfo = subprocess.getoutput("cat /proc/meminfo | egrep 'SwapTotal|\SwapFree' | awk '{print $2}'").splitlines()

        returndata["total"] = swapinfo[0]
        returndata["free"] = swapinfo[1]

        return returndata

    def getCPU(self):
        returndata = {}
        returndata["count"] = subprocess.getoutput("cat /proc/cpuinfo | egrep 'model name' | wc -l")
        returndata["cores"] = subprocess.getoutput("cat /proc/cpuinfo | egrep 'cpu cores' | cut -d':' -f 2 | sort | uniq")
        returndata["model"] = subprocess.getoutput("cat /proc/cpuinfo | egrep 'model name' | cut -d':' -f 2 | sort | uniq")

        return returndata
