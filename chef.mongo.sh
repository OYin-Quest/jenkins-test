#!/bin/bash

mkdir -p /home/skytap/Downloads/tmp
touch /home/skytap/Downloads/test.tmp
ls -l > /home/skytap/Downloads/test.tmp

# copy file from file server to Downloads
# To check whether ssh works
rsync ssh suite@10.6.208.3:"/mnt/share/Share/DataHubFiles/Ocean/jenkins.xml" /home/skytap/Downloads

# Usually sudo command would need to input password
# To check whether password is filled in automatically
echo suite | sudo -S cat /etc/sudoers > /home/skytap/Downloads/sudoers.txt

# To check file list under Downloads
ls /home/skytap/Downloads -l >> /home/skytap/Downloads/sudoers.txt