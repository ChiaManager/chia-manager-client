#!/bin/bash
declare -A updateCMD;
updateCMD[/etc/redhat-release]="yum clean all && yum update -y"
updateCMD[/etc/debian_version]="apt-get update && apt-get upgrade -y"
#osInfo[/etc/arch-release]=pacman
#osInfo[/etc/gentoo-release]=emerge
#osInfo[/etc/SuSE-release]=zypp

found=false
for f in ${!updateCMD[@]}
do
    if [[ -f $f ]];then
        echo Update Command: ${updateCMD[$f]}
        found=true       
    fi
done

if ! ($found);then
    echo "Currently only RedHat (Fedora/Centos/RHEL) or Debian (Debian/Ubuntu/...) based distribtions are supported."
fi

