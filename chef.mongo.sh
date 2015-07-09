#!/bin/bash

mkdir -p /home/skytap/Downloads/tmp
touch /home/skytap/Downloads/test.tmp
ls -l > /home/skytap/Downloads/test.tmp

# copy file from file server to Downloads
# To check whether ssh works
rsync -v suite@10.6.208.3:"/mnt/share/Share/DataHubFiles/Ocean/jenkins.xml" /home/skytap/Downloads > /home/skytap/Downloads/sudoers.txt 2>&1

# Usually sudo command would need to input password
# To check whether password is filled in automatically
echo skytap | sudo -S cat /etc/sudoers >> /home/skytap/Downloads/sudoers.txt 2>&1

# To check file list under Downloads
ls /home/skytap/Downloads -l >> /home/skytap/Downloads/sudoers.txt 2>&1