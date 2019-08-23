#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys, time,os																	#bibliotheque
import RPi.GPIO as Rpi_IO		
import configparser, argparse, memcache
import subprocess
import serial

screen = 22
#LEDR = 26    #B
LEDR = 6     #R
#LEDR = 13	#G		
Rpi_IO.setmode(Rpi_IO.BCM)	   			            #precise que les numeros de broche sont ceux du microprocesseur  (gpio)
Rpi_IO.setwarnings(False)				            #evite l'apparition de messages d'avertissement dans le terminal
Rpi_IO.setup(LEDR,Rpi_IO.OUT)			            #definit la broche la LEDR en sortie
Rpi_IO.setup(screen,Rpi_IO.OUT)	
Rpi_IO.output(LEDR,1)

directory= os.path.dirname(__file__)                                                # get directory
if directory=='':
    directory= os.getcwd()

Config = configparser.ConfigParser()
Config.read(directory+"/config.ini")

parser = argparse.ArgumentParser()                                                   
parser.add_argument("-a", "--action", default='',  help="action for assistant")
parser.add_argument("-c", "--code", default=None,help="Decimal code to send")
args = parser.parse_args()

def set_log(text):
	now = time.strftime('%H:%M %d-%m-%Y', time.localtime())
	file = open(directory+'/log/aya.log','a')
	file.write(now +" -> "+  text+'<br>\n')
	print(" -> "+ text) # now +
	file.close()

if args.action:

	value = args.action.lower()
	#print ('action -> '+value)

	set_log(str(args.action+'R433'+args.code))

	if args.code:
		print ('code -> '+args.code)
		ser = serial.Serial('/dev/ttyAMA0',9600, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, bytesize=serial.EIGHTBITS,timeout=0.5)
		
		if value=="radio" or value=="radio 433" or value=="radio 315":
			#os.system("python3 "+directory+"/api/rpi-rf_send.py "+args.code+" &")
			if value=="radio 433":
				ser.write( str('R433'+args.code).encode() )
			else:
				ser.write( str('R315'+args.code).encode() )
			i=0
			reading=""
			while reading!="FAIT"+args.code  and i<5:
				time.sleep(0.5)
				reading = ser.readline().decode("utf-8") 
				i+=1 
			"""if i==5:
				ser.write( args.code.encode() )
				print("nouvelle tentative")
			else:
				print("fait: "+args.code)"""

		if value=="serial" or value=="radio hc-12":
			#os.system("python3 "+directory+"/api/serialSend.py -c '|"+args.code+"|' &")
			ser.write( args.code.encode() )
			i=0
			reading=""
			while reading!="FAIT"  and i<5 and "ok" not in reading:
				time.sleep(0.5)
				reading = ser.readline().decode("utf-8") 
				print(reading)
				i+=1 
			"""if i==5:
				ser.write( args.code.encode() )
				print("nouvelle tentative")
			else:
				print("fait: "+args.code)"""

	if args.action=="ecranOn":
		Rpi_IO.output(screen,1)
		shared = memcache.Client(['127.0.0.1:11211'], debug=0)
		shared.set('serverOperation', "screenOn")

	if args.action=="ecranOff":
		Rpi_IO.output(screen,0)
		shared = memcache.Client(['127.0.0.1:11211'], debug=0)
		shared.set('serverOperation', "screenOff")

	elif value == 'increasevolume':
		os.system("amixer -q sset Master 5%+")
		print("Vol +")
	elif value == 'decreasevolume':
		os.system("amixer -q sset Master 5%-")
		print("Vol -")
	elif 'volume_set' in value:
		os.system("amixer sset Master "+value[16:]+"%")




	if value[0:6]== 'music_':
		shared = memcache.Client(['127.0.0.1:11211'], debug=0)
		if value == 'music_play':
			
			cmd = shared.get('musicPlayerCmd')
			if cmd=="wait":
				shared.set('musicPlayerCmd', "play")
			else:
				os.system("python3 "+directory+"/musicPlayer.py &") 

		elif value[0:15] == 'music_playlist_':
			shared.set('musicPlayerCmd', "file"+args.action[15:])

		else:
			shared.set('musicPlayerCmd', value[6:])

		time.sleep(1)

	#---------------------------------------------- camera & reboot

	elif value == 'cam_on':
		os.system('cd '+directory+'/api/mjpg-streamer/mjpg-streamer-experimental && ./mjpg_streamer -i "input_uvc.so -d /dev/video0 -f 25 -r 640x480" -o "output_http.so -p 8081" &')

	elif value == 'cam_off':
		os.system("sudo killall mjpg_streamer")


	set_log("action: "+args.action)

	if value == 'reload':
		Rpi_IO.output(LEDR,0)
		shared = memcache.Client(['127.0.0.1:11211'], debug=0)
		shared.set('musicPlayerCmd', 'stop')
		time.sleep(3)
		os.system(directory +"/loadAya.sh")
	elif value == 'kill':
		Rpi_IO.output(LEDR,0)
		shared = memcache.Client(['127.0.0.1:11211'], debug=0)
		shared.set('musicPlayerCmd', 'stop')
		time.sleep(3)
		os.system("sudo killall python3")
	elif value == 'reboot':
		os.system("sudo reboot")
	elif value == 'halt':
		os.system("sudo halt")

else:
	print("aucune action défini")
	Rpi_IO.output(LEDR,0)
	exit(0)

Rpi_IO.output(LEDR,0)
