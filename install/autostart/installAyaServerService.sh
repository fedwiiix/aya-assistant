#!/bin/sh

service_name="ayaServer"
link=$(dirname $(readlink -f $0))"/"

sudo chmod 777 $link$service_name.service

sudo cp $link$service_name.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable $service_name.service
echo fait

#sudo reboot

