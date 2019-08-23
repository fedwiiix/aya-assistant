#!/bin/bash

sudo chmod 777 /dev/ttyAMA0 

link=$(dirname $(readlink -f $0))

echo "clean python"
sudo killall python3
sleep 1

echo "load aia server"

echo "<br><br>--------------------------------------------------------------<br>               load aia<br>--------------------------------------------------------------<br>" >> $link/log/aya.log

$link/server.py &

$link/serialReciever.py &

$link/keyWordDetect.py &

$link/aya.py &



