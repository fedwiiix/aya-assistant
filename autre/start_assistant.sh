#!/bin/bash

assistant_directory='/home/pi/aya_server'


source /etc/bash.bashrc
source ~/.bashrc

#cat /etc/aiyprojects.info

#cd ~/AIY-voice-kit-python
cd ~/aya_server
source /home/pi/AIY-projects-python/env/bin/activate

echo "Domotix Environnement"

sudo python3 $assistant_directory/cherrypy_server.py &
sudo python $assistant_directory/radio_receiver.py &

src/aya.py  &
