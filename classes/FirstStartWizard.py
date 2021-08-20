import logging

from node.NodeConfig import NodeConfig
from node.NodeHelper import NodeHelper

log = logging.getLogger()


class FirstStartWizard:
    def __init__(self):
        log.info("Starting setup wizard")

        self.chiaConfigParser = NodeConfig()
        self.is_first_start = False
        self.current_step = 1

    def step1(self):
        log.info("Checking params in chia-node.ini")
        log.debug(f"Websocketserver: {self.chiaConfigParser.get_connection()}")

        if NodeHelper.yes_no_question("Is this correct?"):
            log.info("Fine - now testing connection to server and proceed with first login.")
            self.current_step = 2
            return True

        log.info("Please correct the information in your chia-node.ini")
        return False

    def step2(self, command):
        key = list(command.keys())[0]

        if "data" in command[key] and "newauthhash" in command[key]["data"]:
            log.info(f"Got authhash '{command[key]['data']['newauthhash']}' from API.")
            log.info("Writing new hash to config file.")
            self.chiaConfigParser.update_config("NodeInfo", "authhash", command[key]["data"]["newauthhash"])
            self.current_step = 3
            return True

        return False

    def step3(self, command):
        key = list(command.keys())[0]

        if key == "loginStatus" and (
                command[key]["status"] == 0 or command[key]["status"] == "005004012" or command[key][
            "status"] == "005004002"):
            return True

        return False

    def getFirststartStep(self):
        return int(self.current_step)

    def setFirstStart(self, status):
        self.is_first_start = status

    def getFirstStart(self):
        return self.is_first_start
