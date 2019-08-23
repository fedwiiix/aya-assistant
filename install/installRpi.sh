#!/bin/bash
# johnwiiix53@gmail.com
# or...s
#


# https://humanizing.tech/diy-raspberry-pi-touchscreen-d27165942bb0

if [ "$EUID" -ne 0 ]
  then echo "Please run as root"
  exit
fi

#sudo AIY-projects-python/scripts/install-alsa-config.sh


#sudo apt-get update
#sudo apt-get upgrade


# web

#sudo apt-get install apache2 # php5
#sudo apt-get install mysql-server phpmyadmin
#sudo apt-get install php
#sudo chmod -R 777 /var/www

# wiring

#sudo apt-get install git-core
#git clone git://git.drogon.net/wiringPi
#cd wiringPi
#sudo ./build

# Python install

sudo apt-get install python3-pip
#sudo apt-get upgrade pip3
sudo -H pip3 install --upgrade pip
#sudo apt-get install python3-serial
sudo pip3 install serial
python -m pip install pyserial
#sudo chmod 777 /dev/ttyAMA0
sudo pip3 install weather-api
sudo pip3 install geotext
sudo pip3 install cherrypy
sudo pip3 install googletrans
sudo pip3 install request
# webcam vs python3

pip3 install opencv-python
sudo apt-get installer libatlas-base-dev

pip3 install configparser

pip3 install cython pyOpenSSL


sudo apt-get install memcached python3-memcache


sudo pip3 install python-vlc
sudo apt-get install vlc

# pi_switch
#sudo pip3 install pi_switch
#python2
#git clone https://github.com/lexruee/pi-switch-python.git
#cd pi-switch-python
#sudo python setup.py install

#sudo pip3 install rpi-rf	# api send radio




#sudo nano /etc/sudoers
#www-data ALL=(ALL) NOPASSWD: ALL
#sudo echo "www-data ALL=(ALL) NOPASSWD: ALL" >> /etc/sudoers



#temperature sensor DHT22
#git clone https://github.com/adafruit/Adafruit_Python_DHT.git && cd Adafruit_Python_DHT
#sudo python setup.py install



# webcam server
# activer
sudo echo "bcm2835-v4l2" >> /etc/modules
#lister les cam dans /dev/video
v4l2-ctl --list-devices
#sudo apt-get install python3-picamera
# raspistill -o cam.jpg

# web cam server 
sudo apt-get -y install subversion libjpeg8-dev imagemagick libav-tools cmake
git clone https://github.com/jacksonliam/mjpg-streamer.git
cd mjpg-streamer/mjpg-streamer-experimental
export LD_LIBRARY_PATH=.
make
# cd mjpg-streamer/mjpg-streamer-experimental && ./mjpg_streamer -i "input_uvc.so -d /dev/video0" -o "output_http.so -p 8765"

# capture video
#sudo apt-get install ffmpeg
#ffmpeg -f v4l2 -framerate 25 -video_size 640x480 -i /dev/video0 output.mkv



# moc
sudo apt-get install moc



#sudo nano /etc/asound.conf
#sudo cp /etc/asound.conf .
#sudo chmod 777 /etc/asound.conf

#echo '
#pcm.!default {
#  type asym
#  capture.pcm "mic"
#  playback.pcm "speaker"
#}
#pcm.mic {
#  type plug
#  slave {
#    pcm "hw:1,0"
#  }
#}
#pcm.speaker {
#  type plug
#  slave {
#    pcm "hw:0,0"
#  }
#} '>> /etc/asound.conf


#sudo nano /boot/config.txt
#uncomment
#dtparam=audio=on



echo '


you must edit the following file:

sudo nano /boot/config.txt

# Enable audio (loads snd_bcm2835)
dtparam=audio=on
#dtoverlay=i2s-mmap
dtoverlay=googlevoicehat-soundcard


add this line: sudo chmod 777 /dev/ttyAMA0
	in : sudo nano /etc/rc.local



After choose good sound card with alsamixer

Good luck!

# ######################################## Serial

cd /dev/ && ls -l    # get serial0

ps -ef | grep tty    # if problems


# enable serial and disable serial for shell

# ######################################## 

sudo nano /etc/rc.local
add 
gpio -g mode 22 out
gpio -g write 22 1

'


