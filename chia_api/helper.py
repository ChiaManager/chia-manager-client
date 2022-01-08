import json
import dataclasses
from typing import Any

from chia_api.constants import WalletType, ServicesForGroup

class EnhancedJSONEncoder(json.JSONEncoder):
    """
    Encodes bytes as hex strings with 0x, and converts all dataclasses to json.
    """

    def default(self, o: Any):
        if dataclasses.is_dataclass(o):
            return o.to_json_dict()
        elif isinstance(o, WalletType):
            return o.name
        elif hasattr(type(o), "__bytes__"):
            return f"0x{bytes(o).hex()}"
        elif isinstance(o, bytes):
            return f"0x{o.hex()}"
        elif isinstance(o, ServicesForGroup):
            return str(o.value)
        return super().default(o)


def dict_to_json_str(o: Any) -> str:
    """
    Converts a python object into json.
    """
    json_str = json.dumps(o, cls=EnhancedJSONEncoder, sort_keys=True)
    return json_str