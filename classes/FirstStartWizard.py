from .ChiaConfigParser import ChiaConfigParser
from .ConsoleFileOutputWriter import ConsoleFileOutputWriter

class FirstStartWizard:
    def __init__(self):
        self.consoleFileOutputWriter = ConsoleFileOutputWriter(True)
        self.consoleFileOutputWriter.writeToConsoleAndFile(0, "Starting setup wizard")
        self.firststart = False
        self.firststartstep = 1

    def step1(self):
        self.chiaConfigParser = ChiaConfigParser()
        coninfo = self.chiaConfigParser.get_connection()
        self.consoleFileOutputWriter.writeToConsoleAndFile(0, "Checking params in chia-client.ini")
        self.consoleFileOutputWriter.writeToConsoleAndFile(0, "Websocketserver: {}".format(coninfo))

        if self.yes_no_question("Is this correct?"):
            self.consoleFileOutputWriter.writeToConsoleAndFile(0, "Fine - now testing connection to server and proceed with first login")
            self.firststartstep = 2
            return True
        else:
            self.consoleFileOutputWriter.writeToConsoleAndFile(0, "Please correct the information in your chia-client.ini")
            return False

    def step2(self, command):
        key = list(command.keys())[0]

        if "data" in command[key] and "newauthhash" in command[key]["data"]:
            self.consoleFileOutputWriter.writeToConsoleAndFile(0, "Got authhash '{}' from API.".format(command[key]["data"]["newauthhash"]))
            self.consoleFileOutputWriter.writeToConsoleAndFile(0, "Writing new hash to config file.")
            self.chiaConfigParser.updateConfig("NodeInfo","authhash",command[key]["data"]["newauthhash"])
            self.firststartstep = 3
            return True
        else:
            return False

    def step3(self, command):
        key = list(command.keys())[0]

        if key == "loginStatus" and (command[key]["status"] == 0 or command[key]["status"] == "005004012" or command[key]["status"] == "005004002"):
            return True
        else:
            return False

    def yes_no_question(self, question):
        yes = set(['yes','y', 'ye', ''])
        no = set(['no','n'])

        while True:
            choice = input("{} y = Yes, n = No: ".format(question)).lower()
            if choice in yes:
                return True
            elif choice in no:
                return False
            else:
               self.consoleFileOutputWriter.writeToConsoleAndFile(0, "&quot;Please respond with 'yes' or 'no'\n&quot")

    def getFirststartStep(self):
        return int(self.firststartstep)

    def setFirstStart(self, status):
        self.firststart = status

    def getFirstStart(self):
        return self.firststart
