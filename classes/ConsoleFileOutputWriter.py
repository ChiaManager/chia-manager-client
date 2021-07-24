import logging, os
from datetime import datetime
from pathlib import Path

class ConsoleFileOutputWriter:
    def __init__(self, ignorecheck):
        rootpath = Path(os.path.realpath(__file__)).parent
        logpath = "{}/../log".format(rootpath)
        logfile = "{}/chia_node_client.log".format(logpath)
        if ignorecheck is not True: self.checkLogDirectoryAndFile(logpath, logfile)

        logging.basicConfig(filename='{}/../log/chia_node_client.log'.format(os.path.dirname(os.path.realpath(__file__))), encoding='utf-8', level=logging.DEBUG, format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')

    def writeToConsoleAndFile(self, type, message):
        msgtypestring = ""
        if type == 0:
            msgtypestring = "[INFO]"
            logging.info("{} {}".format(msgtypestring, message))
        elif type == 1:
            msgtypestring = "[WARN]"
            logging.warning("{} {}".format(msgtypestring, message))
        elif type == 2:
            msgtypestring = "[CRIT]"
            logging.error("{} {}".format(msgtypestring, message))
        else:
            msgtypestring = "[UNKN]"

        print("{} {} {}".format(self.getDateString(), msgtypestring, message))

    def checkLogDirectoryAndFile(self, logpath, logfile):
        self.writeToConsoleAndFile(0, "Checking if log folder and file is existing.")

        if os.path.exists(logpath):
            self.writeToConsoleAndFile(0, "Log folder ({}) exists.".format(logpath))
        else:
            self.writeToConsoleAndFile(0, "Log folder does not exists. Creating it({}).".format(logpath))
            os.makedirs(logpath)

        if os.path.exists(logfile):
            self.writeToConsoleAndFile(0, "Log file ({}) exists.".format(logfile))
        else:
            self.writeToConsoleAndFile(1, "Log file does not exists. Creating empty log.")
            open(logfile, 'w+')
            self.writeToConsoleAndFile(1, "Log file created.")

    def getDateString(self):
        now = datetime.now()
        return now.strftime("%d.%m.%Y %H:%M:%S")
