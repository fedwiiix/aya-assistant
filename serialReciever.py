#!/usr/bin/env python3

import configparser
import requests, json, os
from requests.auth import HTTPDigestAuth

import RPi.GPIO as Rpi_IO

LEDB = 26    #B
Rpi_IO.setmode(Rpi_IO.BCM)	   			            
Rpi_IO.setwarnings(False)		            
Rpi_IO.setup(LEDB,Rpi_IO.OUT)	

import serial,time

ser = serial.Serial('/dev/ttyAMA0',9600, parity=serial.PARITY_NONE, 
				stopbits=serial.STOPBITS_ONE, bytesize=serial.EIGHTBITS,timeout=0.5)



directory= os.path.dirname(__file__)                                                # get directory
if directory=='':
    directory= os.getcwd()

Config = configparser.ConfigParser()
Config.read(directory+"/config.ini")
webserveradress = Config["webServer"]['webserveradress']	
headers = {'User-Agent': 'Mozilla/5.0 Chrome/39.0.2171.95 Safari/537.36'}
authVal=HTTPDigestAuth(Config["webServer"]['user'], Config["webServer"]['pass'])


music_cmds = [['Play', 'play'],['Stop', 'stop'],['Pause', 'pause'],['Previous', 'previous'],['Next', 'next'],
['Volume +', 'increasevolume'],['Volume -', 'decreasevolume']]

devices = [( '', '', '', '' )]
telecommande = [( '', '', '' )]
music = [( '', '' )]

r = requests.get(webserveradress+"database/getDbApi.php?request=all_tables", auth=authVal, headers=headers)
decoded = json.loads((r.content).decode("utf-8"))

for x in decoded['appareils']:
    code = x['code_radio'].split('/')
    code2 = code[0]
    if len(code)==2:
        code2 = code[1]
    devices.append(( x['id_appareil'], code[0], code2, x['mode'].lower() ))


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
                telecommande.append(( x['code_telecommande'], y[1], y[3] ))
            else:
                telecommande.append(( x['code_telecommande'], y[2], y[3] ))

telecommande.remove(( '', '', '' ))     # rm des 1er elements indesirables
music.remove(( '', '' ))
del devices

def set_log(text):
    now = time.strftime('%H:%M %d-%m-%Y', time.localtime())
    file = open(directory+'/log/aya.log','a')
    file.write(now +" -> "+  text+'<br>\n')
    print(" -> "+ text) # now +
    file.close()

set_log("lancement de serialSend.py")

codeFind=0
radioCmd=""
while True:

    try:
        reading = ser.readline().decode("utf-8")
        if reading!="":

            print(reading)
            decoded = json.loads(str(reading))
            print(decoded)

            if "IR" in decoded:
                radioCmd=decoded["IR"]

            elif "Radio" in decoded:
                radioCmd=decoded["Radio"]
            else:
                break

            for x in telecommande:
                if x[0] == radioCmd:
                    Rpi_IO.output(LEDB,1)
                    print('Command reconnu:')
                    #os.system("python3 "+directory+"/api/rpi-rf_send.py "+x[1]+" &")
                    print(x)
                    if x[2]=="radio 433":
                        ser.write( str('R433'+x[1]).encode() )
                    else:
                        ser.write( str('R315'+x[1]).encode() )
                    i=0
                    while reading!="FAIT"+x[1]  and i<4:
                        time.sleep(0.5)
                        reading = ser.readline().decode("utf-8") 
                        i+=1                   

                    ser.flush()
                    set_log("code Radio reconnu: "+radioCmd+" send: "+x[1]+" - appareil")
                    time.sleep(1)
                    Rpi_IO.output(LEDB,0)
                    codeFind=1
                    break

            if codeFind==0:
                for x in music:
                    if x[0] == radioCmd:
                        Rpi_IO.output(LEDB,1)
                        print('Command reconnu:')
                        os.system("python3 "+directory +"/action.py --action '" +x[1]+ "' &")
                        set_log("code Radio reconnu: "+radioCmd+" commande: "+x[1]+" - musique")
                        time.sleep(1)
                        Rpi_IO.output(LEDB,0)
                        codeFind=1
                        break

            if codeFind==0:
                set_log("code Radio: "+radioCmd)
            else:
                codeFind=0
        
    except Exception as e:
        set_log('<b style="color:red">reception error:</b> '+ str(e))
        

    time.sleep(0.02)

