#!/bin/bash
#################################################
#                                               #
# Chia Web Node client installer by @lucaaust.  #
# Version: 0.1.0                                #
#                                               #
#################################################

################################
#Global needed variables start #
################################
ERRCOLOR=$(tput setaf 1)
NOCOLOR=$(tput sgr0)
INFTXT=$(tput setaf 4)[INF]$(tput sgr0)
SUCTXT=$(tput setaf 2)[SUC]$(tput sgr0)
ERRTXT=$(tput setaf 1)[ERR]$(tput sgr0)
WARTXT=$(tput setaf 3)[WAR]$(tput sgr0)

SCRIPT_PATH=`realpath "$0"`
CHIA_NODE_CLIENT_DIR=`dirname "$SCRIPT_PATH"`
CURRENT_USER=`whoami`

declare -A updateCMD;
updateCMD[/etc/redhat-release]="sudo dnf clean all && sudo dnf update"
updateCMD[/etc/debian_version]="sudo apt-get update && sudo apt-get upgrade"
#osInfo[/etc/arch-release]=pacman
#osInfo[/etc/gentoo-release]=emerge
#osInfo[/etc/SuSE-release]=zypp

##############################
#Global needed variables end #
##############################

echo "#############################################################"
echo -e "${INFTXT}Starting installation procedure for the chia node client."
echo -e "${ERRCOLOR}!!!!!! Please do not abort this installation. !!!!!! $NOCOLOR"
sleep 5
echo -e "${INFTXT}Checking if system is supported..."

found=false
for f in ${!updateCMD[@]}
do
    if [[ -f $f ]];then
        os=$(cat $f)
        echo -e "${SUCTXT}Found supported OS $os."
        updateCMD=${updateCMD[$f]}
        found=true       
    fi
done

if ! ($found);then
    echo -e "${ERRTXT}Currently only RedHat (Fedora/Centos/RHEL) or Debian (Debian/Ubuntu/...) based distribtions are supported."
fi

echo -e "${INFTXT}Checking Python version..."

version=$(python3 -V 2>&1 | grep -Po '(?<=Python )(.+)')
parsedVersion=$(echo "${version//./}")
pipexec="pip3"
pythonexec="python3"

if [[ "$parsedVersion" -lt "380" && "$parsedVersion" -ge "370" ]]
then 
    echo -e "${SUCTXT}Valid Python version found! [$version]"
else
    echo -e "${WARTXT}The default python3 executable has a not supported version ($version). Python 3.7.x is required!"
    echo -e "${INFTXT}Checking if python3.7 executable can be found..."
    command -v python3.7 >/dev/null 2>&1
    python_exec_found=$?
    if [ $python_exec_found == 0 ];then
        which_python=$( which python3.7 )
        version=$($which_python -V 2>&1 | grep -Po '(?<=Python )(.+)')
        parsedVersion=$(echo "${version//./}")

        if [[ "$parsedVersion" -lt "380" && "$parsedVersion" -ge "370" ]];then
            echo -e "${SUCTXT}Found python 3.7 installation at ${which_python} (Version $version)."
        else
            echo -e "${ERRTXT}Did not find any supported python version on this system. Skipping installation."
            exit 1
        fi
    fi
fi

#
# Install pipenv package
#
echo -e "${INFTXT}Install pipenv package..."
pip install pipenv >/dev/null 2>&1
pip_exec_status=$?
if [ $pip_exec_status == 0 ];then
    echo -e "${SUCTXT}Done."
else
    echo -e "${ERRTXT}Could not install pipenv. Aborting..."
    exit 1
fi

#
# Recheck install of pipenv package
#
echo -e "${INFTXT}Double-check pipenv installatation for chia node client..."
pipenv --version >/dev/null 2>&1
if [ $? -eq 0 ]; then
    echo -e "${SUCTXT}Found Python pipenv package."
else
    echo -e "${ERRTXT}Could not found Python pipenv package! Please install with 'pip install pipenv' and start install.sh again."
    exit 1
fi

#
# Update system packages
#
echo -e "${INFTXT}Updating System using command '$updateCMD'."
eval "$updateCMD" >/dev/null 2>&1
updateCMDstatus=$?
if [ $updateCMDstatus -eq 0 ]; then
    echo -e "${SUCTXT}Done."
else
    echo -e "${ERRTXT}The installation procedure failed. Please try again. Aborting..."
    exit 1
fi

#
# Installing pipenv
#
echo "${INFTXT}Install newest pipenv for chia-node-client..."
pipenv install --python 3.7 >/dev/null 2>&1
pipenvInstallStatus=$?
if [ $pipenvInstallStatus -eq 0 ]; then
    echo -e "${SUCTXT}Done."
else
    echo -e "${ERRTXT}The installation procedure failed. Please try again. Aborting..."
    exit 1
fi

#
# Create config if not exists
#
echo "${INFTXT}Creating new chia node config if not alread existing..."
if test -f "$CHIA_NODE_CLIENT_DIR/config/node.ini"; then
    echo -e "${INFTXT}Found existing config. Skipping..."
else
    # Get server settings to write config
    echo -e "${INFTXT}Please state the following asked information:"
    read -p "${INFTXT}Enter Server URL/IP: " server_url
    while [[ $server_url = "" ]]; do
        echo "${INFTXT}The Server URL/IP is requiered!"
        read -p "Enter Server URL/IP: " server_url
    done

    read -p "${INFTXT}Enter Server Port (443): " server_port
    if [[ $server_port = "" ]] ;then server_port=443; fi

    read -p "${INFTXT}Enter socketdir: (/chiamgmt)" socketdir
    if [[ $socketdir = "" ]] ;then socketdir='/chiamgmt'; fi

    read -p "${INFTXT}Enter chia-blockchain folder path (/home/$(whoami)/chia-blockchain):" chia_blockchain_path
    if [[ $chia_blockchain_path = "" ]] ;then chia_blockchain_path="/home/$CURRENT_USER/chia-blockchain"; fi

    echo "${INFTXT}Writing new config..."

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

configwritten=$?
if [ $configwritten -eq 0 ]; then
    echo -e "${SUCTXT}Done."
else
    echo -e "${WARTXT}The config file could not be written. Skipping..."
fi

#
# Install script as service
#
read -p "${INFTXT}Install Chia Node Client as Service? [Y/N]" -n 1 -r
echo    # (optional) move to a new line
if [[ $REPLY =~ ^[Yy]$ ]]
then        
    echo -e "${INFTXT}Install as Service.."
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
    echo -e "${INFTXT}Install Service. Done!"

    echo -e "${INFTXT}Reloading daemon, enabling and start $service_name.."
    sudo systemctl daemon-reload
    sudo systemctl enable --now $service_name
    echo -e "${INFTXT}Reloading daemon, enabling and start $service_name.. Done!"

fi

echo -e "${INFTXT}Thank you $CURRENT_USER for using our chia-node-client :)"
echo -e "${INFTXT}Have a nice day! Bye.."
