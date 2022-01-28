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
SYSTEMD_INSTALL_PATH="/etc/systemd/system/"

REQUIRED_PYTHON_VERSION = "3.9"
MINPYTHON="390"
MAXPYTHON="31200"
PYTHON_VERSIONS=("" "3" "3.9" "39" "390")

declare -A updateCMD;
updateCMD[/etc/redhat-release]="sudo dnf clean all && sudo dnf update -y"
updateCMD[/etc/debian_version]="sudo apt-get update && sudo apt-get upgrade -y"
#osInfo[/etc/arch-release]=pacman
#osInfo[/etc/gentoo-release]=emerge
#osInfo[/etc/SuSE-release]=zypp

##############################
#Global needed variables end #
##############################

if [ $CURRENT_USER == "root" ];then
    echo -e "${WARTXT}Please do not install this script as root. Aborting."
    return 1
fi

echo -e "$(tput setaf 2)
MMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMWKKWMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMM
MMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMNOk0NMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMM
MMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMN0xxxONMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMM
MMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMWN0kxxxxOXWMMMMMMMMMMMMMMMMMMMMMMMMMMMMM
MMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMWXKOxxxxxxxOXWMMMMMMMMMMMMMMMMMMMMMMMMMMMM
MMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMWKkxxxxxxxxxxONMMMMMMMMMMMMMMMMMMMMMMMMMMMM
MMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMWNOxxxxxxxxkkxxx0NMMMMMMMMMMMMMMMMMMMMMMMMMMM
MMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMWKkxxxxxxxxxkOOxxkKWMMMMMMMMMMMMMMMMMMMMMMMMMM
MMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMWXOxxxxxxxxxxxx0KkxxONMMMMMMMMMMMMMMMMMMMMMMMMMM
MMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMWKkxxxxxxxxxxxxx0XOxxkXMMMMMMMMMMMMMMMMMMMMMMMMMM
MMMMMMMMMMMMMMMMMMMMMMMMMMMMMWN0xxxxxdxxxxxdxxxKNOxdxKWMMMMMMMMMMMMMMMMMMMMMMMMM
MMMMMMMMMMMMMMMMMMMMMMMMMMMMWXOxdddxddddddddddkXNOddx0WMMMMMMMMMMMMMMMMMMMMMMMMM
MMMMMMMMMMMMMMMMMMMMMMMMMMMMXOdddddddddddddddxONNOddxKWMMMMMMMMMMMMMMMMMMMMMMMMM
WWMMMMMMMMMMMMMMMMMMMMMMMMMW0xdddddddddddddddkXWKxddkXMMMMMMMMMMMMMMMMMMMMMMMMMM
XKNMMMMMMMMMMMMMMMMMMMMMMMMNOdddddddddddddddx0WNOdddONMMMMMMMMMMMMMMMMMMMMMMMMMM
0kOXWMMMMMMMMMMMMMMMMMMMMMMXkdddddddddddddddONN0dddkXMMMMMMMMMMMMMMMMMMMMMMMMMMM
OxxkOKNWMMMMMMMMMMMMMMMMMMMNOdddddddddddoddONN0xddxKWMMMMMMMMMMMMMMMMMMMMMMMMMMM
kxxxxxO0XWMMMMMMMMMMMMMMMMMW0dooooooooooodONN0dooxKWMMMMMMMMMMMMMMMMMMMMMMMMMMMM
kxxxxxxxkOKXWMMMMMMMMMMMMMMMKxooooooooodxONXOdodkXWMMMMMMMMMMMMMMMMMMMMMMMMMMMMM
xxxxxxxxxxxkOKXWMMMMMMMMMMMMWOoooooooox0NNKxoodONMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMM
xxxxxxxxxxxxxxxO0XWMMMMMMMMMMXxooooookXXKOdookXWMMMMMWWNWMMMMMNXNNWMMMMMMMMMMMMM
xxxxxkkxxxxxxxxxxxk0XNWMMMMMMWKdllox0NKxoooxKWMMMMMMN0OkOXWWWXOxkkXWMMMMMMMMMMMM
kxxxxOOxxxxxxxxxxxxxxk0XNWMMMMWKddOXXOooox0NMMMWMMMWXkxxxkOOkkxxxxOXNWWXXNWMMMMM
OxxxxOKkxxxxxxxxxxxddddxk0XWMMMWXXNKxod0XNMMMNK0KXX0kxdxxxxxxxxxxxxxOOOkxkKWMMMM
0xxxxkKKkxxxddddddddddddddx0NWMMMW0ddONMMMMMNOddddddddddddxxxxxxxxxxxxxxxkXWMMMM
Xkxxxx0NKkxdddddddddddddddddkKWMMKxkXWMMMMMMWXkdoddddddxO0KKXXKK0OkxxxxxxkKWWMMM
WKxdddxKNXkxdddddddddddddddddxKWW00NMMMMMMMWWKxooooodkKNWMMMMMMMWWX0kxxxxxkO00KN
MW0xdddxKWN0xdddddddddddddddddkXWNWMMMMMWXOOkdooooox0NMMMMMMMMMMMMMWNOxxxxxxxxx0
MMW0xdddx0WWXkddddddddddddddood0WMMMMMMNXkllllllood0WMMMMMMMMMMMMMMMMNOxxxxxxOKN
MMMWKkdddxOXWNKkddddddoooooooookXMMMMMMWNXOxolllllkNMMMMMMMMMMMMMMMMMWKxdddxxKWM
MMMMWXOxdddx0NWNKkddooooooooooodKMMMMMMMMMMXdcclllkNMMMMMMMMMMMMMMMMMMXkddddxOXN
MMMMMMWXOddodxOXWWXOxdoooooooood0WMMMMMMMWN0occcccdKMMMMMMMMMMMMMMMMMW0dddddddxk
MMMMMMMMWXOxdoodkKNWNKOxoooooooo0WMMMMMMMXdc::cccccxXWMMMMMMMMMMMMMMWKxdddddxxkO
MMMMMMMMMMWNKkxooodk0NWNKOxdollo0WMMMMMMMNxlllc::cccoOXWMMMMMMMMMMWXOdoooodxKNNW
MMMMMMMMMMMMMWNKOxooodk0XWWXKOxkXMMMMMMMMMNXXXkl::::ccok0KXNNNNXK0kdooooood0WMMM
MMMMMMMMMMMMMMMMWNX0kxoooxOXWWWWWMMMMMMMMMMMMMNx:::::::cclloddoolllllloooooxKWMM
MMMMMMMMMMMMMMMMMMMMMWX0kxoox0NMMMMMMMMMMMMMMMKl;;;::::::::cccccccllloxOkxdONMMM
MMMMMMMMMMMMMMMMMMMMMMMMMWX0kxxKWMMMMMMMMMMMMMN0dox00koc:::::ccccccldKWMWNNWMMMM
MMMMMMMMMMMMMMMMMMMMMMMMMMMMWNKOXWMMMMMMMMMMMMMMWWWMMMXo;;:oO00OdcclkNMMMMMMMMMM
MMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMNNWMMMMMMMMMMMMMMMMMMMMNxc:cOWMMWXxxOXWMMMMMMMMMM$(tput sgr0)"
echo -e "
################################################################################
#           Node client install script for Chia Manager                        #
#                       BY lucaaust and OLED1                                  #
#                                                                              #                            
#           Project Sources:                                                   #
#           Client: https://github.com/OLED1/chia-node-client                  #
#           Server: https://github.com/OLED1/chia-web-gui                      #
#                                                                              #
#           Please submit feature requests and issues there if you have some.  #
#           Thank you for using our project \xf0\x9f\x98\x80                                 #
################################################################################"
echo -e "${INFTXT}Starting installation procedure for the chia node client."
echo -e "${ERRCOLOR}!!!!!! Please do not abort this installation. !!!!!! $NOCOLOR"
sleep 5
echo -e "${INFTXT}Checking if system is supported..."

#
# OS Check
#
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
    return 1
fi

#
# Python version check
#
echo -e "${INFTXT}Checking for suitable Python version."
pythonExecPath=""
pythonVersion=0
pipExecPath=""
# TODO: remove loop, 'python' is only for python2
for version in "${PYTHON_VERSIONS[@]}";
do
    echo -e "${INFTXT}Checking if python$version executable can be found."
    which_python=$( which python$version )
    python_found=$?

    if [ $python_found == 0 ];then
        found_python_version=$(python$version -V 2>&1 | grep -Po '(?<=Python )(.+)')
        parsed_python_version=$(echo "${found_python_version//./}")
        echo -e "${SUCTXT}python$version executable existing."
        echo -e "${INFTXT}Checking version."

        if [[ "$parsed_python_version" -lt $MAXPYTHON && "$parsed_python_version" -ge $MINPYTHON ]];then
            echo -e "${SUCTXT}python $version satisfies required version $REQUIRED_PYTHON_VERSION. Detected $found_python_version at $which_python."
            echo -e "${INFTXT}Checking if pip$version can be found."
            which_pip=$( which pip$version )
            pip_found=$?

            if [ $pip_found == 0 ];then            
                pythonExecPath=$which_python
                pipExecPath=$which_pip
                pythonVersion=$($which_python -V 2>&1 | grep -Po '(?<=Python )(.+)')
                echo -e "${SUCTXT}Associated pip$version found."
                break
            else
                echo -e "${WARTXT}pip$version seems not to be installed."
            fi
        else
            echo -e "${WARTXT}Python $version does not satisfy required version $REQUIRED_PYTHON_VERSION. Detected $found_python_version." 
        fi
    else
      echo -e "${WARTXT}python$version not existing..."  
    fi
done

if [ $pythonVersion == 0 ];then
    echo -e "${ERRTXT}Did not detect any supported python version on this system. Skipping installation. Python $REQUIRED_PYTHON_VERSION.x is required."
    return 1
fi

#
# Install pipenv package
#
echo -e "${INFTXT}Install pipenv package..."
$pipExecPath install pipenv >/dev/null 2>&1
pip_exec_status=$?
if [ $pip_exec_status == 0 ];then
    echo -e "${SUCTXT}Done."
else
    echo -e "${ERRTXT}Could not install pipenv. Aborting..."
    return 1
fi

#
# Recheck install of pipenv package
#
echo -e "${INFTXT}Double-check pipenv installation for chia node client..."
pipenv --version >/dev/null 2>&1
if [ $? -eq 0 ]; then
    echo -e "${SUCTXT}Found Python pipenv package."
else
    echo -e "${ERRTXT}Could not found Python pipenv package! Please install with '$pipExecPath install pipenv' and start install.sh again."
    return 1
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
    return 1
fi

#
# Installing pipenv
#
echo "${INFTXT}Install newest pipenv for chia-node-client..."
pipenv install --python 3.7 >/dev/null 2>&1
pipenvInstallStatus=$?
if [ $pipenvInstallStatus == 0 ]; then
    echo -e "${SUCTXT}Done."
else
    echo -e "${ERRTXT}The installation procedure failed. Please try again. Aborting..."
    return 1
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
if [[ $REPLY =~ ^[Yy]$ ]];
then        
    echo -e "${INFTXT}Install as Service.."
    service_name='chia-node-client.service'
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
WantedBy = multi-user.target
EOF
    

    sudo mv $service_name ${SYSTEMD_INSTALL_PATH}${service_name}

    if test -f "${SYSTEMD_INSTALL_PATH}${service_name}"; then
        echo -e "${SUCTXT}Install Service. Done."
    else
        echo -e "${ERRTXT}Install Service. Failed. Skipping..."
    fi

    selinux_installed=$(which getenforce)
    selinux_found=$?
    if [ $selinux_found -eq 0 ]; then
        echo -e "${INFTXT}Found installed SeLinux ($selinux_installed). Restoring defaults in ${SYSTEMD_INSTALL_PATH}${service_name}"
        sudo restorecon -vR ${SYSTEMD_INSTALL_PATH}${service_name} >/dev/null 2>&1
        echo -e "${SUCTXT}Done."
    fi

    echo -e "${INFTXT}Reloading daemon, enabling and start $service_name..."
    sudo systemctl daemon-reload
    sudo systemctl enable --now $service_name
    echo -e "${INFTXT}Reloading daemon, enabling and start $service_name... Done!"

fi

echo -ne "${INFTXT}Thank you $CURRENT_USER for using our chia-node-client \xf0\x9f\x98\x80 \n"
echo -e "${INFTXT}Have a nice day! Bye..."
