#!/bin/bash

# You need to install sshpass before using this script

# Set the devices here
devices=(demowatchtower01 demowatchtower02 demowatchtower03 demowatchtower05 demowatchtower06 demowatchtower08 demowatchtower09 demowatchtower10 demowatchtower11 demowatchtower12 demowatchtower13 demowatchtower14 demowatchtower15)

# Step 1: Generate a new key if it doesn't exist already
cat /dev/zero | ssh-keygen -q -N "" >> /dev/null

# Step 2: Iterate through devices above 
for idx in ${!devices[*]}
do

    printf "\nSetting up %s\n" ${devices[$idx]}
    
    # Step 3: Do magic
    # This command appends the contents of id_rsa.pub from your computer to authorized_keys on the device. 
    # sshpass makes passing the password easier. 
    # -o StrictHostKeyChecking=no adds the hosts to known_hosts file directly thus skipping the part where you need to type "yes" to ssh into a device for the first time
    # The rest is straightforward
    cat ~/.ssh/id_rsa.pub | sshpass -p "MomWatches" ssh -o StrictHostKeyChecking=no mom@${devices[$idx]}.local 'cat >> .ssh/authorized_keys'
    
    printf "Done!\n"
done
