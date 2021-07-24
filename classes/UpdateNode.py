from .ConsoleFileOutputWriter import ConsoleFileOutputWriter
from .ChiaConfigParser import ChiaConfigParser
from io import StringIO
from io import BytesIO
from zipfile import ZipFile
from urllib.request import urlopen
from datetime import datetime
from distutils.dir_util import copy_tree

import os, requests, time, subprocess, json, shutil, sys
from configparser import ConfigParser
from pathlib import Path

class UpdateNode:
    def __init__(self):
        self.status = {}
        self.consoleFileOutputWriter = ConsoleFileOutputWriter(True)
        self.chiaconfigparser = ChiaConfigParser()

    def updateNode(self, link, version):
        self.setStatus(1, "Starting Update.", 0, 2)
        self.consoleFileOutputWriter.writeToConsoleAndFile(0, "Starting Update.")

        scriptpath = Path(os.path.realpath(__file__))
        currdate = datetime.now()

        print("Scriptpath {}".format(scriptpath))

        overall = True
        if self.createBackup(scriptpath, currdate):
            if self.downloadZIP(link, version):
                if self.unzipUpdate(version, scriptpath):
                    if self.copyLogAndConfig(version, scriptpath):
                        if self.testNewUpdate(version, scriptpath):
                            self.finishUpdate(version, scriptpath)
                        else:
                            self.revertChanges(version, scriptpath, currdate)
                            overall = False
                    else:
                        overall = False
                else:
                    overall = False
            else:
                overall = False
        else:
            overall = False


        if overall:
            self.setStatus(10, "Processed Update.", 0, 0)
            self.consoleFileOutputWriter.writeToConsoleAndFile(0, "Sucessfully processed update.")
            return ""
        else:
            self.setStatus(10, "Processed Update.", 1, 1)
            self.consoleFileOutputWriter.writeToConsoleAndFile(1, "Failed processing update.")
            return ""


    def createBackup(self, scriptpath, currdate):
        self.setStatus(2, "Creating Backup", 2, 2)
        self.consoleFileOutputWriter.writeToConsoleAndFile(0, "Creating Backup.")

        rootpath = scriptpath.parent.parent.parent
        scriptversion = self.chiaconfigparser.get_script_info()
        rootfoldername = os.path.basename(scriptpath.parent.parent)

        fromdir = "{}/{}".format(rootpath, rootfoldername)
        todir = "{}/{}-{}-{}-bkp".format(rootpath, rootfoldername, scriptversion, currdate.strftime("%d.%m.%Y-%H:%M:%S"))
        copyied = copy_tree(fromdir, todir)

        if os.path.exists(todir):
            self.setStatus(2, "Creating Backup (Success)", 0, 2)
            self.consoleFileOutputWriter.writeToConsoleAndFile(0, "Creating Backup: Success.")
            return True
        else:
            self.setStatus(2, "Creating Backup (Failed)", 1, 1)
            self.consoleFileOutputWriter.writeToConsoleAndFile(1, "Creating Backup: Failed.")
            return False

    def downloadZIP(self, link, version):
        self.setStatus(3, "Downloading ZIP", 2, 2)
        self.consoleFileOutputWriter.writeToConsoleAndFile(0, "Downloading ZIP.")

        results = requests.get(link)
        downloadpath = "/tmp/chia_python_client_{}.zip".format(version)
        with open(downloadpath, 'wb') as f:
            f.write(results.content)

        if os.path.exists(downloadpath):
            self.setStatus(3, "Downloading ZIP (Success)", 0, 2)
            self.consoleFileOutputWriter.writeToConsoleAndFile(0, "Downloading ZIP: Success.")
            return True
        else:
            self.setStatus(3, "Downloading ZIP (Failed)", 1, 1)
            self.consoleFileOutputWriter.writeToConsoleAndFile(0, "Downloading ZIP: Failed.")
            return False

    def unzipUpdate(self, version, scriptpath):
        self.setStatus(4, "Unzipping Update", 2, 2)
        self.consoleFileOutputWriter.writeToConsoleAndFile(0, "Unzipping Update.")

        downloadpath = "/tmp/chia_python_client_{}.zip".format(version)
        targetpath = "{}/../chia_python_client_{}".format(scriptpath.parent.parent, version)

        with ZipFile(downloadpath, 'r') as zipObj:
            zipObj.extractall('{}'.format(targetpath))

        if os.path.exists(targetpath):
            self.setStatus(4, "Unzipping Update (Success)", 0, 2)
            self.consoleFileOutputWriter.writeToConsoleAndFile(0, "Unzipping Update: Success.")
            return True
        else:
            self.setStatus(4, "Unzipping Update (Failed)", 1, 1)
            self.consoleFileOutputWriter.writeToConsoleAndFile(1, "Unzipping Update: Failed.")
            return False

    def copyLogAndConfig(self, version, scriptpath):
        self.setStatus(5, "Copy Log and Config", 2, 2)
        self.consoleFileOutputWriter.writeToConsoleAndFile(0, "Copy Log and Config")

        scriptversion = self.chiaconfigparser.get_script_info()
        rootfoldername = os.path.basename(scriptpath.parent.parent)
        now = datetime.now()
        fromdir = "{}/../{}".format(scriptpath.parent.parent,rootfoldername)
        todir = "{}/../chia_python_client_{}".format(scriptpath.parent.parent, version)
        logdir = "{}/log".format(fromdir)
        configdir = "{}/config".format(fromdir)

        logcopy = copy_tree("{}/log".format(fromdir), "{}/log".format(todir))
        configcopy = copy_tree("{}/config".format(fromdir), "{}/config".format(todir))

        if os.path.exists("{}/log".format(todir)) and  os.path.exists("{}/config".format(todir)):
            self.setStatus(4, "Copy Log and Config (Success)", 0, 2)
            self.consoleFileOutputWriter.writeToConsoleAndFile(0, "Copy Log and Config: Failed.")
            return True
        else:
            self.setStatus(4, "Copy Log and Config (Failed)", 1, 1)
            self.consoleFileOutputWriter.writeToConsoleAndFile(1, "Copy Log and Config: Failed.")
            return False


    def testNewUpdate(self, version, scriptpath):
        self.setStatus(5, "Testing Update", 2, 2)
        self.consoleFileOutputWriter.writeToConsoleAndFile(0, "Testing Update.")

        targetpath = "{}/../chia_python_client_{}/chia_mgmt_node.py".format(scriptpath.parent.parent, version)
        cmd = "python {} testupdate".format(targetpath)

        if os.path.exists(targetpath):
            proc = subprocess.Popen(['python', targetpath,  'testupdate'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            callback = json.loads(proc.communicate()[0].splitlines()[-1].decode("utf-8"))

            if callback["status"] == 0:
                self.setStatus(5, "Testing Update (Success)", 0, 2)
                self.consoleFileOutputWriter.writeToConsoleAndFile(0, "Testing Update: Success.")
                return True
            else:
                self.setStatus(5, "Testing Update (Failed)", 1, 1)
                self.consoleFileOutputWriter.writeToConsoleAndFile(1, "Testing Update: Failed.")
                return False
        else:
            self.setStatus(5, "Testing Update (Failed)", 1, 1)
            self.consoleFileOutputWriter.writeToConsoleAndFile(1, "Testing Update: Failed.")
            return False

    def finishUpdate(self, version, scriptpath):
        self.setStatus(6, "Finishing Update", 2, 2)
        self.consoleFileOutputWriter.writeToConsoleAndFile(0, "Finishing Update.")

        config_object = ConfigParser()
        olddirroot = os.path.basename(scriptpath.parent.parent)
        olddir = scriptpath.parent.parent

        updatedir = "{}/chia_python_client_{}".format(scriptpath.parent.parent.parent, version)
        newdir = "{}/{}".format(scriptpath.parent.parent.parent, olddirroot)
        newconfig = "{}/config/chia-client.ini".format(updatedir)

        if os.path.exists(newconfig):
            config_object.read(newconfig)
            scriptversion = config_object["ScriptInfo"]["version"] = version

            with open(newconfig, "w") as conf:
                config_object.write(conf)

            if olddirroot != "dev_client":
                shutil.rmtree(olddir)
                os.rename(updatedir, newdir)
            else:
                print("Not deleting development client")

            self.consoleFileOutputWriter.writeToConsoleAndFile(0, "This script will now be restarted in background.")
            execpath = "{}/chia_mgmt_node.py".format(newdir)
            subprocess.Popen(['python', execpath], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            sys.exit()

            self.setStatus(6, "Finishing Update (Success)", 0, 2)
            self.consoleFileOutputWriter.writeToConsoleAndFile(0, "Finishing Update: Success.")
        else:
            self.setStatus(6, "Finishing Update (Success)", 1, 1)
            self.consoleFileOutputWriter.writeToConsoleAndFile(1, "Finishing Update: Success.")

    def revertChanges(self, version, scriptpath, currdate):
        self.setStatus(9, "Update failed... Revert changes.", 2, 2)
        self.consoleFileOutputWriter.writeToConsoleAndFile(9, "Update failed... Revert changes.")

        rootpath = scriptpath.parent.parent.parent
        scriptversion = self.chiaconfigparser.get_script_info()
        rootfoldername = os.path.basename(scriptpath.parent.parent)

        updatedir = "{}/chia_python_client_{}".format(scriptpath.parent.parent.parent, version)
        backupdir = "{}/{}-{}-{}-bkp".format(rootpath, rootfoldername, scriptversion, currdate.strftime("%d.%m.%Y-%H:%M:%S"))

        shutil.rmtree(updatedir)
        shutil.rmtree(backupdir)

        self.setStatus(9, "Reverted Changes (Success)", 0, 2)
        self.consoleFileOutputWriter.writeToConsoleAndFile(9, "Reverted Changes: Success.")

    def getStatus(self):
        return self.status

    #status = 0 (Success), 1 (Failed), 2 (Processing)
    def setStatus(self, step, message, status, overallstatus):
        self.status[step] = {
            "status" : status,
            "message" : "{} {}".format(self.getDateString(), message)
        }
        self.status["overall"] = overallstatus

    def getDateString(self):
        now = datetime.now()
        return now.strftime("%d.%m.%Y %H:%M:%S")
