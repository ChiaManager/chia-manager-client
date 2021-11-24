import logging
import os
import subprocess
import time

import psutil

log = logging.getLogger()


class SystemInfo:

    def get_system_info(self) -> dict:
        sys_info = {
            'system': {
                'load': self.get_load_avg(),
                'memory': self.get_memory_info(),
                'swap': self.get_swap_info(),
                'filesystem': self.get_filesystem_info(),
                'cpu': self.get_cpu_info(),
                'uptime': time.time() - psutil.boot_time()
            }
        }

        log.debug(f"sys_info: {sys_info}")
        return sys_info

    @staticmethod
    def get_load_avg() -> dict:
        load_avg = psutil.getloadavg()
        return {
            '1min': load_avg[0],
            '5min': load_avg[1],
            '15min': load_avg[2]
        }

    @staticmethod
    def get_filesystem_info() -> list:
        filesystems = subprocess.getoutput("df | tail -n +2").splitlines()

        file_system_info = []
        for filesystem in filesystems:
            # add all not empty entries
            file_system_info.append([e for e in filesystem.split(" ") if e != ""])

        return file_system_info

    @staticmethod
    def get_memory_info() -> dict:
        mem_info = psutil.virtual_memory()

        return {
            'total': mem_info.total,
            'free': mem_info.free,
            'buffers': mem_info.buffers,
            'cached': mem_info.cached,
            'shared': mem_info.shared
        }

    @staticmethod
    def get_swap_info() -> dict:
        swap_info = psutil.swap_memory()
        return {
            'total': swap_info.total,
            'free': swap_info.free
        }

    @staticmethod
    def get_cpu_info() -> dict:
        # count and cores are the same ?
        return {
            "count": os.cpu_count(),
            'physical_cores': psutil.cpu_count(),
            'logical_cores': psutil.cpu_count(logical=True),
            "cores": subprocess.getoutput(
                "cat /proc/cpuinfo | egrep 'cpu cores' | cut -d':' -f 2 | sort | uniq"),
            "model": subprocess.getoutput(
                "cat /proc/cpuinfo | egrep 'model name' | cut -d':' -f 2 | sort | uniq")
        }
