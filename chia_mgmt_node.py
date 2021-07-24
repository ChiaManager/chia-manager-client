from classes.ChiaConfigParser import ChiaConfigParser
from classes.RequestBuilder import RequestBuilder
from classes.FirstStartWizard import FirstStartWizard
from classes.CommandInterpreter import CommandInterpreter
from classes.ConsoleFileOutputWriter import ConsoleFileOutputWriter
from classes.ChiaInterpreter import ChiaInterpreter
from pathlib import Path

import websocket, os, socket, json, yaml, sys, getopt, shutil, psutil, subprocess

interrupt = False

try:
    import thread
except ImportError:
    import _thread as thread
    import time

def on_message(ws, message):
    command = json.loads(message)

    if firstStartWizard.getFirstStart():
        key = list(command.keys())[0]
        consoleFileOutputWriter.writeToConsoleAndFile(0, "Got message from API on command {}: {}".format(key, command[key]["message"]))

        if firstStartWizard.getFirststartStep() == 2:
            if firstStartWizard.step2(command):
                consoleFileOutputWriter.writeToConsoleAndFile(0, "Finished init wizard successfully. Waiting for authentication on backend.")
                chiaConfigParser = ChiaConfigParser()
                time.sleep(1)
                authhash = chiaConfigParser.get_node_info()["authhash"]
                reqdata = requestBuilder.getFormatedInfo(authhash, "ownRequest", "ChiaMgmt\\Nodes\\Nodes_Api", "Nodes_Api", "loginStatus", {})
                ws.send(json.dumps(reqdata))
            else:
                consoleFileOutputWriter.writeToConsoleAndFile(2, "An error occured during first start init")
        elif firstStartWizard.getFirststartStep() == 3:
            if firstStartWizard.step3(command):
                consoleFileOutputWriter.writeToConsoleAndFile(0, "Finished authentication successfully. Please refer to above message.")
                firstStartWizard.setFirstStart(False)
            else:
                consoleFileOutputWriter.writeToConsoleAndFile(2, "An error occured interpreting request string from api.")
    else:
        commandInterpreterReturn = commandInterpreter.interpretCommand(command)
        if commandInterpreterReturn is not None:
            if 0 in commandInterpreterReturn:
                for arrkey in commandInterpreterReturn:
                    ws.send(json.dumps(commandInterpreterReturn[arrkey]))
            else:
                ws.send(json.dumps(commandInterpreterReturn))



def on_error(ws, error):
    consoleFileOutputWriter.writeToConsoleAndFile(2, "Websocket client closed unexpected.")
    if interrupt is not True:
        restartScript()

def on_close(self, ws, error):
    consoleFileOutputWriter.writeToConsoleAndFile(2, "Websocket client closed unexpected.")

def on_open(ws):
    if firstStartWizard.getFirstStart():
        authhash = ""
    else:
        authhash = chiaConfigParser.get_node_info()["authhash"]

    consoleFileOutputWriter.writeToConsoleAndFile(0, "Requesting login information from api.")
    reqdata = requestBuilder.getFormatedInfo(authhash, "ownRequest", "ChiaMgmt\\Nodes\\Nodes_Api", "Nodes_Api", "loginStatus", {})
    ws.send(json.dumps(reqdata))

    def run(*args):
        while True:
            time.sleep(5)
    thread.start_new_thread(run, ())

def start_websocket_client():
    constring = chiaConfigParser.get_connection()
    #websocket.enableTrace(True)

    ws = websocket.WebSocketApp(constring,
                              on_open = on_open,
                              on_message = on_message,
                              on_error = on_error,
                              on_close = on_close)

    ws.run_forever()

def yes_no_question(question):
    yes = set(['yes','y', 'ye', ''])
    no = set(['no','n'])

    while True:
        choice = input("{} y = Yes, n = No: ".format(question)).lower()
        if choice in yes:
            return True
        elif choice in no:
            return False
        else:
           print("&quot;Please respond with 'yes' or 'no'\n&quot");

def interpretArguments(arguments):
    validarguments = ["testupdate"]

    for argument in arguments:
        if argument in validarguments:
            if argument == "testupdate":
                try:
                    from classes.TestUpdate import TestUpdate
                    testupdate = TestUpdate()
                    testupdate.testUpdate()
                    print("\n")
                    print(json.dumps({"status": 0, "message": "Update test successfull."}))
                except Exception as e:
                    print("\n")
                    print(json.dumps({"status": 1, "message": "Update test failed."}))

                sys.exit()

def already_running():
    num_instance = 0
    for q in psutil.process_iter():
        if 'python' in q.name():
            if len(q.cmdline()) > 1 and os.path.basename(__file__) in q.cmdline()[1]:
                num_instance += 1
    return num_instance > 1

def restartScript():
    consoleFileOutputWriter.writeToConsoleAndFile(0, "This script will be restarted in background in 5sec.")
    scriptpath = Path(os.path.realpath(__file__))
    time.sleep(5)
    subprocess.Popen(['python', scriptpath], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    sys.exit()

if __name__ == "__main__":
    consoleFileOutputWriter = ConsoleFileOutputWriter(False)
    chiaConfigParser = ChiaConfigParser()
    firstStartWizard = FirstStartWizard()
    chiaInterpreter = ChiaInterpreter()
    consoleFileOutputWriter.writeToConsoleAndFile(0, "Starting ChiaNode python script Version: {} and Chia Version: {}.".format(chiaConfigParser.get_script_info(), chiaInterpreter.getChiaVersionAndInstallPath()["version"]))

    try:
        if already_running() == 1:
            consoleFileOutputWriter.writeToConsoleAndFile(1, "An instance of this script is already running. Ignoring...")


        consoleFileOutputWriter.writeToConsoleAndFile(0, "Starting websocket client.")
        commandInterpreter = CommandInterpreter(consoleFileOutputWriter)
        requestBuilder = RequestBuilder()

        if chiaConfigParser.get_node_info()["authhash"] == "":
            firstStartWizard.setFirstStart(True)
            firstStartWizard.step1()

        if firstStartWizard.getFirstStart() is not True:
            interpretArguments(sys.argv[1:])

        start_websocket_client()
    except KeyboardInterrupt:
        pass
    finally:
        consoleFileOutputWriter.writeToConsoleAndFile(0, "Ctrl+C was pressed. Stopping Script. Bye.")
        interrupt = True
