from enum import IntEnum, Enum

# Source: https://github.com/Chia-Network/chia-blockchain/blob/main/chia/wallet/util/wallet_types.py
class WalletType(IntEnum):
    STANDARD_WALLET = 0
    RATE_LIMITED = 1
    ATOMIC_SWAP = 2
    AUTHORIZED_PAYEE = 3
    MULTI_SIG = 4
    CUSTODY = 5
    COLOURED_COIN = 6
    RECOVERABLE = 7
    DISTRIBUTED_ID = 8
    POOLING_WALLET = 9

class ServicesForGroup(Enum):
    ALL = "chia_harvester chia_timelord_launcher chia_timelord chia_farmer chia_full_node chia_wallet".split()
    NODE = "chia_full_node",
    HARVESTER = "chia_harvester",
    FARMER = "chia_harvester chia_farmer chia_full_node chia_wallet".split()
    FARMER_NO_WALLET = "chia_harvester chia_farmer chia_full_node".split()
    FARMER_ONLY = "chia_farmer",
    TIMELORD = "chia_timelord_launcher chia_timelord chia_full_node".split(),
    TIMELORD_ONLY = "chia_timelord",
    TIMELORD_LAUNCHER_ONLY = "chia_timelord_launcher",
    WALLET = "chia_wallet chia_full_node".split()
    WALLET_ONLY = "chia_wallet",
