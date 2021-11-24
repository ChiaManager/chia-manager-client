#!/bin/bash

SCRIPT_PATH=`realpath "$0"`
CHIA_NODE_CLIENT_DIR=`dirname "$SCRIPT_PATH"`
CURRENT_USER=`whoami`

echo Checking Python version..
version=$(python3 -V 2>&1 | grep -Po '(?<=Python )(.+)')
echo $version
parsedVersion=$(echo "${version//./}")
if [[ "$parsedVersion" -lt "380" && "$parsedVersion" -ge "370" ]]
then 
    echo "Valid Python version found! [$version]"
else
    echo "Invalid Python version! Python 3.7.x is required!"
    exit 1
fi

echo "Install pipenv package.."
pip3 install pipenv
echo "Done!"

pipenv --version
if [ $? -eq 0 ]; then
    echo "Found Python pipenv package."
else
    echo "Could not found Python pipenv package! Please install with 'pip install pipenv' and start install.sh again."
    exit 1
fi


echo Updating System..
sudo apt update -y && sudo apt dist-upgrade -y
echo Done!


echo Install newest pipenv for chia-node-client..
pipenv install --python 3.7
echo Done!

# create config if not exist
if test -f "$CHIA_NODE_CLIENT_DIR/config/node.ini"; then
    echo "Found existing config.."
else
    # Get server settings to write config
    read -p "Enter Server URL/IP: " server_url
    while [[ $server_url = "" ]]; do
        echo "The Server URL/IP is requiered!"
        read -p "Enter Server URL/IP: " server_url
    done

    read -p "Enter Server Port (443): " server_port
    if [[ $server_port = "" ]] ;then server_port=443; fi

    read -p "Enter socketdir: (/chiamgmt)" socketdir
    if [[ $socketdir = "" ]] ;then socketdir='/chiamgmt'; fi

    read -p "Enter chia-blockchain folder path (/home/$(whoami)/chia-blockchain):" chia_blockchain_path
    if [[ $chia_blockchain_path = "" ]] ;then chia_blockchain_path="/home/$CURRENT_USER/chia-blockchain"; fi

    sudo cat > config/node.ini << EOF
[Connection]
server = $server_url
port = $server_port
socketdir = $socketdir

[Chia]
chia_blockchain_path = $chia_blockchain_path

[Logging]
log_level = ERROR
log_backup_count = 3
log_path = $CHIA_NODE_CLIENT_DIR
EOF
fi

read -p "Install Chia Node Client as Service? [Y/N]" -n 1 -r
echo    # (optional) move to a new line
if [[ $REPLY =~ ^[Yy]$ ]]
then        
    echo "Install as Service.."
    service_name='chia-node-client.service'
    echo $service_name
    sudo cat > $service_name << EOF
[Unit]
Description = Chia Node Client Service
After = network.target

[Service]
Type = simple
WorkingDirectory = $CHIA_NODE_CLIENT_DIR
ExecStart = $(pipenv --venv)/bin/python run_node_client.py
User = $(whoami)
Restart = on-failure
SyslogIdentifier = chia-node-client

[Install]
WantedBy = user.target
EOF
    
    sudo mv $service_name /etc/systemd/system/$service_name
    echo "Install Service. Done!"

    echo "Reloading daemon, enabling and start $service_name.."
    sudo systemctl daemon-reload
    sudo systemctl enable --now $service_name
    echo "Reloading daemon, enabling and start $service_name.. Done!"

fi

echo "Thank you $CURRENT_USER for using our chia-node-client :)"
echo "Have a nice day! Bye.."
