#!/bin/bash


# Set the devices here
devices=(demowatchtower01 demowatchtower02 demowatchtower03 demowatchtower05 demowatchtower06 demowatchtower07 demowatchtower08 demowatchtower09 demowatchtower10 demowatchtower11 demowatchtower12 demowatchtower13 demowatchtower14 demowatchtower15)

# TODO
# Preflight checklist
# Check log folder 

# Pull image
# Start logging
# Display interesting stats
# End logging

printf "\nStarting logging session\n"
printf " =========================================================== \n"
printf "|%20s%10s|%5s%15s%8s|\n" "Device" "" "" "Logs Folder" ""
printf "|===========================================================|\n"
for idx in ${!devices[*]}
do
    #if ! ssh host command
    #then
    #echo "SSH connection or remote command failed"
    #fi

    output=`ssh -q mom@${devices[$idx]}.local '[ -d /data/logs ] && echo Yes|| echo No' || echo Error`
    printf "|%20s%10s|%5s%15s%8s|\n" ${devices[$idx]} "" "" $output ""
done
printf " =========================================================== \n"

echo "Do you wish to continue?"
select yn in "Yes" "No"; do
    case $yn in
        Yes ) echo "Moving to the next step"; break;;
        No ) exit;;
    esac
done


