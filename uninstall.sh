#!/bin/bash

# written by @lucaaust

SYSTEMD_INSTALL_PATH="/etc/systemd/system/"
SERVICE_NAME='chia-manager-client.service'

INF=$(tput setaf 4)[INF]$(tput sgr0)
SUC=$(tput setaf 2)[SUC]$(tput sgr0) 
ERR=$(tput setaf 1)[ERR]$(tput sgr0) 
WAR=$(tput setaf 3)[WAR]$(tput sgr0) 

read -p "${INFTXT} Are you sure you want to delete the Chia-Manager client? [Y/N]" -n 1 -r
echo    # (optional) move to a new line
if [[ $REPLY =~ ^[Nn]$ ]];
then 
    echo -e "${INF} Aborted!"
    return 0
fi


# remove remove node-client pipenv
echo "${INFTXT} Remove pipenv for chia-manager-client..."
pipenv install >/dev/null 2>&1
pipenv_rm_status=$?
if [ $pipenv_rm_status == 0 ]; then
    echo -e "${SUC} Done."
else
    echo -e "${ERR} The remove procedure failed. Please try again. Aborting..."
    return 1
fi



# delete the service if the user has installed it
if test -f "${SYSTEMD_INSTALL_PATH}${SERVICE_NAME}"; then
    echo -e "${INF} Found $SERVICE_NAME. Remove.."
    sudo systemctl stop $SERVICE_NAME
    sudo systemctl disable $SERVICE_NAME
    sudo rm $SYSTEMD_INSTALL_PATH$SERVICE_NAME

    # check if delete was successful
    if test -f "${SYSTEMD_INSTALL_PATH}${SERVICE_NAME}"; then
        echo -e "${ERR} Failed to delete the ${SERVICE_NAME}"
        return 1
    else
        echo -e "${SUC} Removed ${SERVICE_NAME} successful."
    fi
else
    echo -e "${INF} $SERVICE_NAME not found. Skip.."
fi

echo -e "${SUC} All done! You can now delete the chia-manager-client directory."