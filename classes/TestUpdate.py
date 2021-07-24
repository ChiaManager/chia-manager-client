from .ConsoleFileOutputWriter import ConsoleFileOutputWriter
from .CommandInterpreter import CommandInterpreter

import socket, json

class TestUpdate:
    def __init__(self):
        self.consoleFileOutputWriter = ConsoleFileOutputWriter(True)
        self.commandInterpreter = CommandInterpreter(self.consoleFileOutputWriter)
        self.commandstotest = ["loginStatus", "queryCronData", "nodeUpdateStatus"]
        self.consoleFileOutputWriter.writeToConsoleAndFile(0, "Test new installation.")

    def testUpdate(self):
        excounter = 0
        for command in self.commandstotest:
            try:
                self.consoleFileOutputWriter.writeToConsoleAndFile(0, "Found Command {}.".format(command))
                fullcommand = {
                    command : {
                        "status" : 0,
                        "message" : "Test Update",
                        "data" : {
                            "hostname" : socket.gethostname(),
                            "nodetype" : "Just testing update."
                        }
                    }
                }
                interpreter = self.commandInterpreter.interpretCommand(fullcommand)
            except Exception:
                excounter += 1
                return false

        return False
