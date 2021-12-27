import socket
from pathlib import Path
from typing import Any


class NodeHelper:

    @staticmethod
    def yes_no_question(question):
        yes = ('yes', 'y', 'ye', '')
        no = ('no', 'n')

        while True:
            choice = input(f"{question} \n Y/N [Y]:").lower()
            if choice in yes:
                return True
            elif choice in no:
                return False
            else:
                print("&quot;Please respond with 'yes' or 'no'\n&quot")

    @staticmethod
    def get_formated_info(auth_hash: str, socket_action: str, namespace: str, method: str,
                          data: Any) -> dict:
        return {
            "node": {
                'nodeinfo':
                    {
                        'hostname': socket.gethostname()
                    },
                'socketaction': socket_action
            },
            'request': {
                'logindata': {
                    'authhash': auth_hash
                },
                'data': data,
                'backendInfo': {
                    'namespace': namespace,
                    'method': method
                }
            }
        }

    @staticmethod
    def json_serialize(obj: Any) -> Any:
        if isinstance(obj, Path):
            return obj.as_posix()
