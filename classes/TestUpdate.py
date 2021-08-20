import socket
import logging


log = logging.getLogger()


class TestUpdate:
    def __init__(self):
        self.commandInterpreter = CommandInterpreter()
        self.commandstotest = ["loginStatus", "queryCronData", "nodeUpdateStatus"]
        log.debug("Test new installation.")

    def testUpdate(self):
        excounter = 0
        for command in self.commandstotest:
            try:
                log.debug(f"command: {command}")
                fullcommand = {
                    command: {
                        "status": 0,
                        "message": "Test Update",
                        "data": {
                            "hostname": socket.gethostname(),
                            "nodetype": "Just testing update."
                        }
                    }
                }
                interpreter = self.commandInterpreter.interpretCommand(fullcommand)
            except Exception:
                excounter += 1
                return False

        return False
