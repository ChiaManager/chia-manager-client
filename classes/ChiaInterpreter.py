from .ChiaConfigParser import ChiaConfigParser
from .ConsoleFileOutputWriter import ConsoleFileOutputWriter
import subprocess, os, time

class ChiaInterpreter:
    def __init__(self):
        self.chiaConfigParser = ChiaConfigParser()
        self.consoleFileOutputWriter = ConsoleFileOutputWriter(False)

        chiaPath = self.chiaConfigParser.get_chia_path()
        self.chiaPorts = self.chiaConfigParser.get_chia_ports()
        self.activatePath = "{}/activate".format(chiaPath)
        self.venvPythonPath = "{}/venv/bin/python".format(chiaPath)

    def checkChiaInstallPaths(self):
        self.consoleFileOutputWriter.writeToConsoleAndFile(0, "Checking activate path {} and python venv path {}.".format(self.activatePath, self.venvPythonPath))

        found = True
        if os.path.exists(self.activatePath):
            self.consoleFileOutputWriter.writeToConsoleAndFile(0, "Activate file found")
        else:
            self.consoleFileOutputWriter.writeToConsoleAndFile(0, "Activate file not found.  Please take a look at installation and your config.")
            found = False

        if os.path.exists(self.venvPythonPath):
            self.consoleFileOutputWriter.writeToConsoleAndFile(0, "Python venv file found")
        else:
            self.consoleFileOutputWriter.writeToConsoleAndFile(0, "Python venv file not found. Please take a look at installation and your config.")
            found = False

        return found

    def getChiaVersionAndInstallPath(self):
        returndata = {}
        if self.checkChiaInstallPaths():
            returndata["version"] = os.popen(self.formatChiaCommand("chia version")).read().strip()
            returndata["path"] = self.activatePath

        return returndata

    def getWalletInformations(self):
        returndata = {}

        if self.checkChiaInstallPaths() and self.checkWalletRunning("bool"):
            walletinfos = os.popen(self.formatChiaCommand("chia wallet show")).read().splitlines()

            tempreturn = {}
            count = 0
            for walletinfo in walletinfos:
                if "Wallet height" in walletinfo:
                    tempreturn["walletheight"] = walletinfo.split(":")[1].strip()
                elif "Sync status" in walletinfo:
                    tempreturn["syncstatus"] = walletinfo.split(":")[1].strip()
                elif "Wallet ID" in walletinfo:
                    tempreturn["walletid"] = walletinfo.split()[2].strip()
                    tempreturn["wallettype"] = walletinfo.split()[4].strip()
                elif "-Total Balance" in walletinfo.strip():
                    tempreturn["totalbalance"] = walletinfo.split()[2].strip()
                elif "-Pending Total" in walletinfo.strip():
                    tempreturn["pendingtotalbalance"] = walletinfo.split()[3].strip()
                elif "-Spendable" in walletinfo.strip():
                    tempreturn["spendable"] = walletinfo.split()[1].strip()
                    tempreturn["walletaddress"] = os.popen(self.formatChiaCommand("chia wallet get_address")).read().splitlines()[count]
                    returndata["wallet"] = {}
                    returndata["wallet"][tempreturn["walletid"]] = tempreturn
                    tempreturn = {}
                    count = 1

        self.consoleFileOutputWriter.writeToConsoleAndFile(0, "Returning {}.".format(returndata))
        return returndata

    def getFarmerInformations(self):
        returndata = {}

        if self.checkChiaInstallPaths() and self.checkFarmerRunning("bool"):
            farmerinfos = os.popen(self.formatChiaCommand("chia farm summary")).read().splitlines()
            challenges = os.popen(self.formatChiaCommand("chia farm challenges")).read().splitlines()

            returndata["farm"] = {}

            for farmerinfo in farmerinfos:
                if "Farming status" in farmerinfo:
                    returndata["farm"]["farming_status"] = farmerinfo.split(":")[1].strip()
                elif "Total chia farmed" in farmerinfo:
                    returndata["farm"]["total_chia_farmed"] = farmerinfo.split(":")[1].strip()
                elif "User transaction fees" in farmerinfo:
                    returndata["farm"]["user_transaction_fees"] = farmerinfo.split(":")[1].strip()
                elif "Block rewards" in farmerinfo:
                    returndata["farm"]["block_rewards"] = farmerinfo.split(":")[1].strip()
                elif "Last height farmed" in farmerinfo:
                    returndata["farm"]["last_height_farmed"] = farmerinfo.split(":")[1].strip()
                elif "Plot count" in farmerinfo:
                    returndata["farm"]["plot_count"] = farmerinfo.split(":")[1].strip()
                elif "Total size of plots" in farmerinfo:
                    returndata["farm"]["total_size_of_plots"] = farmerinfo.split(":")[1].strip()
                elif "Estimated network space" in farmerinfo:
                    returndata["farm"]["estimated_network_space"] = farmerinfo.split(":")[1].strip()
                elif "Expected time to win" in farmerinfo:
                    returndata["farm"]["expected_time_to_win"] = farmerinfo.split(":")[1].strip()

        returndata["farm"]["challenges"] = challenges
        self.consoleFileOutputWriter.writeToConsoleAndFile(0, "Returning {}.".format(returndata))

        return returndata

    def checkWalletRunning(self, type):
        self.consoleFileOutputWriter.writeToConsoleAndFile(0, "Checking if wallet service is running.")
        count = int(os.popen(self.formatChiaCommand("netstat -antp 2>/dev/null | grep '{}' | wc -l".format(self.chiaPorts["walletport"]))).read().splitlines()[0])
        if count > 0:
            self.consoleFileOutputWriter.writeToConsoleAndFile(0, "Wallet service running.")
            if type == "json": return { "status" : 0, "message" : "Wallet service running." }
            return True
        else:
            self.consoleFileOutputWriter.writeToConsoleAndFile(1, "Wallet service not running.")
            if type == "json": return { "status" : 1, "message" : "Wallet service not running." }
            return False

    def checkFarmerRunning(self, type):
        self.consoleFileOutputWriter.writeToConsoleAndFile(0, "Checking if farmer service is running.")
        count = int(os.popen(self.formatChiaCommand("netstat -antp 2>/dev/null | grep '{}' | wc -l".format(self.chiaPorts["farmerport"]))).read().splitlines()[0])
        if count > 0:
            self.consoleFileOutputWriter.writeToConsoleAndFile(0, "Farmer service running.")
            if type == "json": return { "status" : 0, "message" : "Farmer service running." }
            return True
        else:
            self.consoleFileOutputWriter.writeToConsoleAndFile(1, "Farmer service not running.")
            if type == "json": return { "status" : 1, "message" : "Farmer service not running." }
            return False

    def farmerServiceRestart(self):
        self.consoleFileOutputWriter.writeToConsoleAndFile(0, "Restarting farmer service.")
        os.popen(self.formatChiaCommand("chia start farmer -r")).read().splitlines()
        os.wait()
        time.sleep(2)
        return self.checkFarmerRunning("json")

    def walletServiceRestart(self):
        self.consoleFileOutputWriter.writeToConsoleAndFile(0, "Restarting wallet service.")
        os.popen(self.formatChiaCommand("chia start wallet -r")).read().splitlines()
        os.wait()
        time.sleep(2)
        return self.checkWalletRunning("json")

    def formatChiaCommand(self, command):
        return 'source {} && {} && deactivate'.format(self.activatePath, command)
