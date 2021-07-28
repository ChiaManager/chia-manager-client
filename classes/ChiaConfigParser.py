from configparser import ConfigParser
from .ConsoleFileOutputWriter import ConsoleFileOutputWriter
from pathlib import Path
import os, sys, time

class ChiaConfigParser:
    config_object = {}

    def __init__(self):
        self.config_object = ConfigParser()
        self.consoleFileOutputWriter = ConsoleFileOutputWriter(True)

        rootpath = Path(os.path.realpath(__file__)).parent
        configpath = "{}/../config".format(rootpath)
        self.configdir = "{}/chia_client.ini".format(configpath)

        self.checkLogAndConfig(configpath, self.configdir)

        self.config_object.read(self.configdir)
        self.set_connection_info()
        self.set_node_info()

    def set_connection_info(self):
        connectioninfo = self.config_object["Connection"]
        self.__sockettype = format(connectioninfo["type"])
        self.__server = format(connectioninfo["server"])
        self.__port = format(connectioninfo["port"])
        self.__socketdir = format(connectioninfo["socketdir"])

    def set_node_info(self):
        nodeinfo = self.config_object["NodeInfo"]
        self.__authhash = format(nodeinfo["authhash"])

    def get_script_info(self):
        return self.config_object["ScriptInfo"]["version"]

    def get_connection(self):
        self.__connection = "{}://{}:{}{}".format(self.__sockettype, self.__server, self.__port, self.__socketdir)
        return self.__connection

    def get_node_info(self):
        node_info_array = {}
        node_info_array["authhash"] = self.__authhash
        return node_info_array

    def get_chia_path(self):
        return self.config_object["Chia"]["chiaactivatepath"]

    def get_chia_ports(self):
        chiaInfo = self.config_object["Chia"]
        ports_array = {}
        ports_array["walletservice"] = chiaInfo["walletservice"]
        ports_array["farmerservice"] = chiaInfo["farmerservice"]
        ports_array["harvesterservice"] = chiaInfo["harvesterservice"]
        return ports_array

    def updateConfig(self, section, key, value):
        self.config_object[section][key] = value;
        with open(self.configdir, "w") as conf:
            self.config_object.write(conf)

        self.config_object.read(self.configdir)

    def checkLogAndConfig(self, configpath, configfile):
        self.consoleFileOutputWriter.writeToConsoleAndFile(0, "Checking if config folder and file is existing.")
        stopClient = False

        if os.path.exists(configpath):
            self.consoleFileOutputWriter.writeToConsoleAndFile(0, "Config folder ({}) exists.".format(configpath))
        else:
            self.consoleFileOutputWriter.writeToConsoleAndFile(0, "Config folder does not exists. Creating it({}).".format(configpath))
            os.makedirs(configpath)

        if os.path.exists(configfile):
            self.consoleFileOutputWriter.writeToConsoleAndFile(0, "Config file ({}) exists.".format(configfile))
        else:
            self.consoleFileOutputWriter.writeToConsoleAndFile(1, "Config file does not exists. Creating standard config.")
            open(configfile, 'w+')
            self.createDefaultConfig()
            self.consoleFileOutputWriter.writeToConsoleAndFile(1, "Config file created. Client will stop execution. Please setup you config.")
            stopClient = True

        if stopClient:
            time.sleep(2)
            sys.exit()

    def createDefaultConfig(self):
        self.config_object['ScriptInfo'] = {'version': '0.1.1-alpha'}

        self.config_object['Connection'] = {'server': 'chiamgmt.example.com',
                                'port': '443',
                                'socketdir': '/chiamgmt',
                                'type': 'wss'}

        self.config_object['NodeInfo'] = {'authhash': ''}
        self.config_object['Chia'] = {'chiaactivatepath': '',
                                'walletservice' : 'chia_wallet',
                                'farmerservice' : 'chia_farmer',
                                'harvesterservice' : 'chia_harvester'}

        with open(self.configdir, 'w+') as configfile:
            self.config_object.write(configfile)

        self.config_object.read(self.configdir)
