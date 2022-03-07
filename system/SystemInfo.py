import sys
import os
import time
import logging
import subprocess
import platform

from system.constants import WIN_RELEASES

import psutil


log = logging.getLogger()

IS_WINDOWS = sys.platform == 'win32'



class SystemInfo:

    def get_system_info(self) -> dict:
        sys_info = {
            'system': {
                'memory': self.get_memory_info(),
                'swap': self.get_swap_info(),
                'filesystem': self.get_filesystem_info(),
                'cpu': self.get_cpu_info(),
                'uptime': time.time() - psutil.boot_time(),
                'os': self.get_os(),
            }
        }

        log.debug(f"sys_info: {sys_info}")
        return sys_info

    @staticmethod
    def get_os():
        res = {'type': platform.system()}
        if IS_WINDOWS:
                
            win_ver = sys.getwindowsversion()
            maj, min, build = win_ver.platform_version or win_ver[:3]

            res['name'] = WIN_RELEASES.get((maj, min, build)) or win_ver
        else:
            res['name'] = platform.platform()

        return res
    @staticmethod
    def get_filesystem_info() -> list:
        file_system_info = []
        
        for disk in psutil.disk_partitions():
            disk_usage = psutil.disk_usage(disk.device)

            file_system_info.append({
                'device': disk.device,
                'total': disk_usage.total,
                'used': disk_usage.used,
                'free':  disk_usage.free,
                'mountpoint': disk.mountpoint,
                'fs_type': disk.fstype
            })

        return file_system_info

    @staticmethod
    def get_memory_info() -> dict:
        mem_info = psutil.virtual_memory()
        result = {
            'total': mem_info.total,
            'free': mem_info.free,
            'buffers': None,
            'cached': None,
            'shared': None,
        }

        if not IS_WINDOWS:
            result.update({
                'buffers': mem_info.buffers,
                'cached': mem_info.cached,
                'shared': mem_info.shared
            })
        
        return result

    @staticmethod
    def get_swap_info() -> dict:
        swap_info = psutil.swap_memory()
        return {
            'total': swap_info.total,
            'free': swap_info.free
        }

    @staticmethod
    def get_cpu_info() -> dict:
        load_avg = psutil.getloadavg()

        return {
            'count': os.cpu_count(),
            'physical_cores': psutil.cpu_count(),
            'logical_cores': psutil.cpu_count(logical=True),
            'model': platform.processor(),
            'usage': psutil.cpu_percent(),
            'load': {
                '1min': load_avg[0],
                '5min': load_avg[1],
                '15min': load_avg[2]
            }
        }
