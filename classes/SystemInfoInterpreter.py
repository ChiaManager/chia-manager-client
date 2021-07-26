from .ChiaConfigParser import ChiaConfigParser
import subprocess, os, sys

class SystemInfoInterpreter:
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
