# chia-manager-client
The Chia Node Client is the agent part of [chia-web-gui](https://github.com/OLED1/chia-manager).

# Requirements
- RedHat (Fedora/Centos/RHEL) or Debian (Debian/Ubuntu/...) based OS
- Python 3.9 with pip
- non-root user
- Reachable [chia-web-gui](https://github.com/OLED1/chia-web-gui)
- Installed and running [chia-blockchain](https://github.com/Chia-Network/chia-blockchain)
- read acces to the Chia SSL certificates
    `~/.chia/mainnet/config/ssl/full_node/private_full_node.crt` and
    `~/.chia/mainnet/config/ssl/full_node/private_full_node.key`

# Installation
1. Clone this repo
2. Run the `install.sh`