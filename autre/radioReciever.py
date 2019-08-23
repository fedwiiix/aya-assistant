#!/usr/bin/env python3

import argparse, configparser
import signal
import sys
import time
import logging

from rpi_rf import RFDevice

import requests, json, os
from requests.auth import HTTPDigestAuth

import RPi.GPIO as Rpi_IO

LEDB = 26    #B
Rpi_IO.setmode(Rpi_IO.BCM)	   			            
Rpi_IO.setwarnings(False)		            
Rpi_IO.setup(LEDB,Rpi_IO.OUT)	


directory= os.path.dirname(__file__)                                                # get directory
if directory=='':
    directory= os.getcwd()

aya_log_file = directory	+'/log/aya.log'

Config = configparser.ConfigParser()
Config.read(directory+"/config.ini")
webserveradress = Config["webServer"]['webserveradress']	
headers = {'User-Agent': 'Mozilla/5.0 Chrome/39.0.2171.95 Safari/537.36'}
authVal=HTTPDigestAuth(Config["webServer"]['user'], Config["webServer"]['pass'])


music_cmds = [['Play', 'play'],['Stop', 'stop'],['Pause', 'pause'],['Previous', 'previous'],['Next', 'next'],
['Volume +', 'increasevolume'],['Volume -', 'decreasevolume']]

devices = [( '', '', '' )]
telecommande = [( '', '' )]
music = [( '', '' )]

r = requests.get(webserveradress+"database/get_db.php?request=all_tables", auth=authVal, headers=headers)
#print((r.text))
decoded = json.loads((r.content).decode("utf-8"))

for x in decoded['appareils']:
    code = x['code_radio'].split('/')
    code2 = code[0]
    if len(code)==2:
        code2 = code[1]

    devices.append(( x['id_appareil'], code[0], code2 ))


for x in decoded['telecommande_music']:
    i=0
    for y in music_cmds:
        if x['cmd_telecommande'] == y[0]:
            music.append(( x['code_telecommande'], 'music_'+y[1] ))
            i=1
            break
    if i==0:
        music.append(( x['code_telecommande'], 'music_playlist_'+x['cmd_telecommande'] ))

for x in decoded['telecommande']:

    for y in devices:
        if y[0] == x['appareil_telecommande']:
            if x['cmd_telecommande'] == 'On':
                telecommande.append(( x['code_telecommande'], y[1] ))
            else:
                telecommande.append(( x['code_telecommande'], y[2] ))

telecommande.remove(( '', '' ))     # rm des 1er elements indesirables
music.remove(( '', '' ))
del devices


def set_log(text):
    now = time.strftime('%H:%M %d-%m-%Y', time.localtime())
    file = open(aya_log_file,'a')
    file.write(now +" -> "+  text+'<br>\n')
    print(" -> "+ text) # now +
    file.close()


rfdevice = None
# pylint: disable=unused-argument
def exithandler(signal, frame):
    rfdevice.cleanup()
    sys.exit(0)

logging.basicConfig(level=logging.INFO, datefmt='%Y-%m-%d %H:%M:%S',
                    format='%(asctime)-15s - [%(levelname)s] %(module)s: %(message)s', )

parser = argparse.ArgumentParser(description='Receives a decimal code via a 433/315MHz GPIO device')
parser.add_argument('-g', dest='gpio', type=int, default=27,
                    help="GPIO pin (Default: 27)")
args = parser.parse_args()

signal.signal(signal.SIGINT, exithandler)
rfdevice = RFDevice(args.gpio)
rfdevice.enable_rx()
timestamp = None
logging.info("Listening for codes on GPIO " + str(args.gpio))

codeFind=0
while True:
    if rfdevice.rx_code_timestamp != timestamp and len(str(rfdevice.rx_code))>5 and str(rfdevice.rx_proto)=="1":

        try:
            timestamp = rfdevice.rx_code_timestamp
            logging.info(str(rfdevice.rx_code)+" [pulselength "+str(rfdevice.rx_pulselength)+", protocol "+str(rfdevice.rx_proto) + "]")

            for x in telecommande:
                if x[0] == str(rfdevice.rx_code):
                    Rpi_IO.output(LEDB,1)
                    print('Command reconnu:')
                    os.system("python3 "+directory+"/api/rpi-rf_send.py "+x[1]+" &")
                    set_log("code Radio reconnu: "+str(rfdevice.rx_code)+" send: "+x[1]+" - appareil")
                    time.sleep(1)
                    Rpi_IO.output(LEDB,0)
                    codeFind=1
                    break

            if codeFind==0:
                for x in music:
                    if x[0] == str(rfdevice.rx_code):
                        Rpi_IO.output(LEDB,1)
                        print('Command reconnu:')
                        os.system("python3 "+directory +"/action.py --action '" +x[1]+ "' &")
                        set_log("code Radio reconnu: "+str(rfdevice.rx_code)+" commande: "+x[1]+" - musique")
                        time.sleep(1)
                        Rpi_IO.output(LEDB,0)
                        codeFind=1
                        break

            if codeFind==0:
                set_log("code Radio: "+str(rfdevice.rx_code))
            else:
                codeFind=0
        
        except Exception as e:
            set_log('<b style="color:red">reception error:</b> '+ str(e))
        

    time.sleep(0.01)
rfdevice.cleanup()