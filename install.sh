#!/bin/bash
#############################################################
#                                                           #
# Chia-Manager client installer by @lucaaust and @OLED1.   #
# Version: 0.1.0                                            #
#                                                           #
#############################################################

################################
#Global needed variables start #
################################
ERRCOLOR=$(tput setaf 1)
NOCOLOR=$(tput sgr0)
INFTXT=$(tput setaf 4)[INF]$(tput sgr0)
SUCTXT=$(tput setaf 2)[SUC]$(tput sgr0)
ERRTXT=$(tput setaf 1)[ERR]$(tput sgr0)
WARTXT=$(tput setaf 3)[WAR]$(tput sgr0)

##Script config
SCRIPT_PATH=`realpath "${BASH_SOURCE[0]}"`
CHIA_MANAGER_CLIENT_DIR=`dirname "$SCRIPT_PATH"`
CURRENT_USER=`whoami`
SYSTEMD_INSTALL_PATH="/etc/systemd/system/"


##Python config
REQUIRED_PYTHON_VERSION="3.9"
MINPYTHON="390"
MAXPYTHON="31200"
PYTHON_VERSIONS=("" "3" "3.9" "39" "390" "310")


## OS config
USED_OS=

declare -A supportedOS;
supportedOS[/etc/redhat-release]="RedHat"
supportedOS[/etc/lsb-release]="Ubuntu"
supportedOS[/etc/debian_version]="Debian"

declare -A osVersionCommand;
osVersionCommand[RedHat]="cat /etc/redhat-release"
osVersionCommand[Ubuntu]="cat /etc/lsb-release | grep DISTRIB_DESCRIPTION | cut -d'=' -f2 | sed 's/\"//g'"
osVersionCommand[Debian]="cat /etc/debian_version"

eval ${osVersionCommand[Ubuntu]}

declare -A usedOSinstall;
usedOSinstall[RedHat]="dnf install"
usedOSinstall[Ubuntu]="apt-get install"
usedOSinstall[Debian]="apt-get install"

declare -A usedOSinstall;
neededPackages[RedHat]="python3-pip pipenv python3-devel"
neededPackages[Ubuntu]="python3-pip pipenv python3-psutil"
neededPackages[Debian]="python3-pip pipenv python3-psutil"

CHIA_REPO="https://repo.chia.net"
declare -A chiaInstallation;
chiaInstallation[RedHat]="sudo yum install -y yum-utils && \
sudo yum-config-manager --add-repo ${CHIA_REPO}/rhel/chia-blockchain.repo && \
sudo yum install chia-blockchain-cli -y"

chiaInstallation[Ubuntu]="sudo apt-get update && \
sudo apt-get install ca-certificates curl gnupg && \
curl -sL ${CHIA_REPO}/FD39E6D3.pubkey.asc | sudo gpg --dearmor -o /usr/share/keyrings/chia.gpg --yes && \
echo \"deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/chia.gpg] ${CHIA_REPO}/debian/ stable main\" | sudo tee /etc/apt/sources.list.d/chia.list > /dev/null && \
sudo apt-get update && \
sudo apt-get install chia-blockchain-cli -y"

chiaInstallation[Debian]="sudo apt-get update && \
sudo apt-get install ca-certificates curl gnupg && \
curl -sL ${CHIA_REPO}/FD39E6D3.pubkey.asc | sudo gpg --dearmor -o /usr/share/keyrings/chia.gpg --yes && \
echo \"deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/chia.gpg] ${CHIA_REPO}/debian/ stable main\" | sudo tee /etc/apt/sources.list.d/chia.list > /dev/null && \
sudo apt-get update && \
sudo apt-get install chia-blockchain-cli -y"

declare -A usedOSupdate;
updateCMD[RedHat]="sudo dnf clean all && sudo dnf update -y"
updateCMD[Ubuntu]="sudo apt-get update && sudo apt-get upgrade -y"
updateCMD[Debian]="sudo apt-get update && sudo apt-get upgrade -y"
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
#           Chia-Manager install script for Chia Manager                       #
#                       BY lucaaust and OLED1                                  #
#                                                                              #                            
#           Project Sources:                                                   #
#           Client: https://github.com/OLED1/chia-manager-client               #
#           Server: https://github.com/OLED1/chia-manager                      #
#                                                                              #
#           Please submit feature requests and issues there if you have some.  #
#           Thank you for using our project \xf0\x9f\x98\x80                                 #
################################################################################"
echo -e "${INFTXT}Starting installation procedure for the Chia-Manager client."
#sleep 5
echo -e "${INFTXT}Checking if system is supported..."

#
# OS Check
#
echo "---------------------------------------------------------------------------"
found=false
for versfile in ${!supportedOS[@]}
do
    if [[ -f $versfile ]];then
        USED_OS=${supportedOS[$versfile]}
        os_version=$(eval ${osVersionCommand[$USED_OS]})
        echo -e "${SUCTXT}Found supported OS maintainer: $USED_OS. Version: $os_version."
        found=true
        break
    fi
done

if ! ($found);then
    echo -e "${ERRTXT}Currently only RedHat (Fedora/Centos/RHEL) or Debian (Debian/Ubuntu/...) based distribtions are supported."
    exit 1
fi

#
# Last check if the user wants to make changes to the system
#
echo "-------------------------------------------------------------------------------------"
ans_valid=false
while (!($ans_valid)); do
    read -ep "${INFTXT}Upon here you should not abort the following installation steps. Are you really sure? [yY/nN]" yn
    case $yn in 
        [yY] ) echo -e "${INFTXT}Hanging on."; ans_valid=true;;
        [nN] ) echo -e "${INFTXT}Exitting."; ans_valid=true;
            exit 0;;
        * ) echo -e "${WARTXT}Invalid response. [yY/nN]";
    esac
done

#
# Check if Chia blockchain is installed
#
echo "-------------------------------------------------------------------------------------"
echo -e "${INFTXT}Detecting if chia blockchain installed."
echo "-------------------------------------------------------------------------------------"
chia_found=$(which chia)
chia_found=$?

ans_valid=false
chia_installed=1
install_chia_blockchain=1
if [ $chia_found -eq 0 ];then
    echo "Chia Blockchian found. Hanging on..."
else
    while (!($ans_valid)); do
        read -ep "${WARTXT}Chia Blockchain not found. Is it currently installed using another methhod? [yY/nN]" yn
        case $yn in 
            [yY] ) echo -e "${INFTXT}Yes - Hanging on."; ans_valid=true; chia_installed=0;;
            [nN] ) echo -e "${INFTXT}No - Hanging on."; ans_valid=true;;
            * ) echo -e "${WARTXT}Invalid response. [yY/nN]";
        esac
    done

    if [ $chia_installed -eq 1 ];then
        ans_valid=false
        echo -e "${INFTXT}Chia Blockchain needs to be installed and configured in order to run the chia manager agent."
        while (!($ans_valid)); do
            read -ep "${INFTXT}Would you like us to install it? [yY/nN]" yn
            case $yn in 
                [yY] ) echo -e "${INFTXT}Fine. We will start soon."; ans_valid=true; install_chia_blockchain=0;;
                [nN] ) echo -e "${INFTXT}Please install install chia blockchain an rerun this script or let us install it for you."; ans_valid=true;
                    exit 1;;
                * ) echo -e "${WARTXT}Invalid response. [yY/nN]";
            esac
        done
    fi
fi

if [ $chia_installed -eq 1 ] && [ $install_chia_blockchain -eq 0 ];then
    echo -e "${INFTXT}Executing ${chiaInstallation[$USED_OS]}."
    echo -e "${INFTXT}You have 5secs to abort..."
    sleep 5
    echo -e "${INFTXT}Please state root password when asked. "
    eval ${chiaInstallation[$USED_OS]}
fi

#
# Checking requirements and install them if missing 
#
echo "-------------------------------------------------------------------------------------"
echo -e "${INFTXT}Installing all needed packages. Please wait."
echo "-------------------------------------------------------------------------------------"
echo -e "${INFTXT}Executing ${usedOSinstall[$USED_OS]} ${neededPackages[$USED_OS]}. Please state root password when asked."
sudo ${usedOSinstall[$USED_OS]} ${neededPackages[$USED_OS]} -y

#
# Python version check
#
echo "-------------------------------------------------------------------------------------"
echo -e "${INFTXT}Checking for suitable Python version."
echo "-------------------------------------------------------------------------------------"
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
    exit 1
fi

#
# Install pipenv package
#
echo "-------------------------------------------------------------------------------------"
echo -e "${INFTXT}Install needed project dependencie packages..."
echo "-------------------------------------------------------------------------------------"
pip3 install websockets psutil websocket-client==0.44.0
pip_exec_status=$?
if [ $pip_exec_status == 0 ];then
    echo -e "${SUCTXT}Done."
else
    echo -e "${ERRTXT}Could not install needed packages. Aborting..."
    exit 1
fi

#
# Install pipenv package
#
echo "-------------------------------------------------------------------------------------"
echo -e "${INFTXT}Install pipenv packages..."
echo "-------------------------------------------------------------------------------------"
$pipExecPath install pipenv #>/dev/null 2>&1
pip_exec_status=$?
if [ $pip_exec_status == 0 ];then
    echo -e "${SUCTXT}Done."
else
    echo -e "${ERRTXT}Could not install pipenv. Aborting..."
    exit 1
fi

#
# Updating pipenv environment
#
echo "-------------------------------------------------------------------------------------"
echo -e "${INFTXT}Updating pipenv packages..."
echo "-------------------------------------------------------------------------------------"
pipenv update
pip_exec_status=$?
if [ $pip_exec_status == 0 ];then
    echo -e "${SUCTXT}Done."
else
    echo -e "${ERRTXT}Could not update pipenv environment. Aborting..."
    exit 1
fi

#
# Recheck install of pipenv package
#
echo "-------------------------------------------------------------------------------------"
echo -e "${INFTXT}Double-check pipenv installation for chia-manager-client..."
echo "-------------------------------------------------------------------------------------"
pipenv --version #>/dev/null 2>&1
if [ $? -eq 0 ]; then
    echo -e "${SUCTXT}Found Python pipenv package."
else
    echo -e "${ERRTXT}Could not found Python pipenv package! Please install with '$pipExecPath install pipenv' and start install.sh again."
    exit 1
fi

#
# Update system packages
#
echo "-------------------------------------------------------------------------------------"
echo -e "${INFTXT}Updating System using command '$updateCMD'."
echo "-------------------------------------------------------------------------------------"
echo -e "${ERRCOLOR}!!! Do not abort this step. Your system might break. !!! $NOCOLOR"
eval "$updateCMD" #>/dev/null 2>&1
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
echo "-------------------------------------------------------------------------------------"
echo "${INFTXT}Install newest pipenv for chia-manager-client..."
echo "-------------------------------------------------------------------------------------"
pipenv install #>/dev/null 2>&1
pipenvInstallStatus=$?
if [ $pipenvInstallStatus == 0 ]; then
    echo -e "${SUCTXT}Done."
else
    echo -e "${ERRTXT}The installation procedure failed. Please try again. Aborting..."
    exit 1
fi

#
# Create config if not exists
#
echo "-------------------------------------------------------------------------------------"
echo "${INFTXT}Creating new client config if not alread existing..."
echo "-------------------------------------------------------------------------------------"
if test -f "$CHIA_MANAGER_CLIENT_DIR/config/node.ini"; then
    echo -e "${INFTXT}Found existing config. Skipping..."
else
    # Get server settings to write config
    echo -e "${INFTXT}Please state the following asked information:"
    while [[ $server_url = "" ]]; do
        read -p "${INFTXT}Enter Server URL/IP: " server_url
        ping -c 2 $server_url >/dev/null 2>&1
        available=$?
        if [ $available -eq 0 ];then
            echo "${SUCTXT}Host $server_url exists."
        else
            echo "${ERRTXT}Your stated host $server_url does not exist. Please type in another host."
            server_url=
        fi
    done

    while [[ $server_port = "" ]]; do
        read -p "${INFTXT}Enter Server Port (443): " server_port
        if [[ $server_port = "" ]] ;then server_port=443; fi
        nc -zvw5 $server_url $server_port >/dev/null 2>&1
        available=$?
        if [ $available -eq 0 ];then
            echo "${SUCTXT}Host ${server_url}:${server_port} reachable."
        else
            echo "${ERRTXT}Cant connect to ${server_url}:${server_port}. Please state another port."
            server_port=
        fi
    done
    

    while [[ $socketdir = "" ]]; do
        read -p "${INFTXT}Enter socketdir: (/chiamgmt)" socketdir
        if [[ $socketdir = "" ]] ;then socketdir='/chiamgmt'; fi
        http_code=$(curl -m 2 -s -o /dev/null -I -w "%{http_code}" https://${server_url}:${server_port}/${socketdir})
        available=$?
        if [ $available -eq 0 ] && [ $http_code == 405 ];then
            echo "${SUCTXT}Websocket https://${server_url}:${server_port}/${socketdir} reachable (HTTP ${http_code})."
        else
            echo "${ERRTXT}Cant connect to websocket https://${server_url}:${server_port}/${socketdir} (HTTP ${http_code}). Please state another websocket path."
            socketdir=
        fi
    done
    
    echo "${INFTXT}NOTE BEFORE HANGING ON: If you need to execute migration steps you can abort now and rerun this script when finished or wait an press enter when done."
    echo "${INFTXT}Otherwise the blockchain install path will not be found."
    while [[ $chia_blockchain_path = "" ]]; do
        read -p "${INFTXT}Enter chia-blockchain folder path (/home/$(whoami)/.chia):" chia_blockchain_path
        if [[ $chia_blockchain_path = "" ]] ;then chia_blockchain_path="/home/$CURRENT_USER/.chia"; fi

        if [ -d "$chia_blockchain_path" ]; then
            echo "${SUCTXT}Chia blockchain path found."
        else
            echo "${ERRTXT}Unable to find the chia blockchain path ${chia_blockchain_path}. Please state another one."
            chia_blockchain_path=
        fi
    done    

    echo "${INFTXT}Writing new config..."

    sudo cat > config/node.ini << EOF
[Connection]
server = $server_url
port = $server_port
socketdir = $socketdir

[Chia]
chia_blockchain_cli = $chia_blockchain_path

[Logging]
log_level = ERROR
log_backup_count = 3
log_path = $CHIA_MANAGER_CLIENT_DIR
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
echo "-------------------------------------------------------------------------------------"
echo "${INFTXT}Creating systemctl script."
echo "-------------------------------------------------------------------------------------"
read -p "${INFTXT}Install Chia-Manager Client as Service? [Y/N]" -n 1 -r
echo    # (optional) move to a new line
if [[ $REPLY =~ ^[Yy]$ ]];
then        
    echo -e "${INFTXT}Install as Service.."
    service_name='chia-manager-client.service'
    sudo cat > $service_name << EOF
[Unit]
Description = Chia-Manager client service
After = network.target

[Service]
Type = simple
WorkingDirectory = $CHIA_MANAGER_CLIENT_DIR
ExecStart = $(pipenv --venv)/bin/python run_client.py
User = $CURRENT_USER
Restart = on-failure
SyslogIdentifier = chia-manager-client

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

echo -ne "${INFTXT}Thank you $CURRENT_USER for using our Chia-Manager client \xf0\x9f\x98\x80 \n"
echo -e "${INFTXT}Have a nice day! Bye..."
