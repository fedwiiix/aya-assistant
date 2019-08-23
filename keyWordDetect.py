#!/usr/bin/env python3
import os
from pocketsphinx import pocketsphinx
from sphinxbase import sphinxbase
import pyaudio, configparser, time
import RPi.GPIO as Rpi_IO
import memcache
shared = memcache.Client(['127.0.0.1:11211'], debug=0)
shared.set('keyWordDetect', 0)

directory= os.path.dirname(__file__)                                                # get directory
if directory=='':
    directory= os.getcwd()

Config = configparser.ConfigParser()
Config.read(directory+"/config.ini")
keyWord = Config["Global"]['keyWord']



#****************************************************************************************************************

import RPi.GPIO as Rpi_IO
import time

screen = 22
LEDB = 26    #B
LEDR = 6     #R
LEDG = 13	 #G		
Rpi_IO.setmode(Rpi_IO.BCM)	   			            #precise que les numeros de broche sont ceux du microprocesseur  (gpio)
Rpi_IO.setwarnings(False)				            #evite l'apparition de messages d'avertissement dans le terminal
Rpi_IO.setup(LEDR,Rpi_IO.OUT)			            #definit la broche la LED en sortie
Rpi_IO.setup(LEDG,Rpi_IO.OUT)			            
Rpi_IO.setup(LEDB,Rpi_IO.OUT)			            
Rpi_IO.setup(screen,Rpi_IO.OUT)	

BpGpio = 27    										# gpio bp											
#Rpi_IO.setup(BpGpio,Rpi_IO.IN,Rpi_IO.PUD_UP)		#configuration broches en entree routine d'interruption
Rpi_IO.setup(BpGpio,Rpi_IO.IN) #,Rpi_IO.PUD_UP)		#configuration broches en entree routine d'interruption
def Appui_BP (BP):								    # si le bp est presser

    i=0
    phase=0
    Rpi_IO.output(LEDR,0)
    Rpi_IO.output(LEDG,0)
    Rpi_IO.output(LEDB,0)
    
    while (Rpi_IO.input(BP)==1):  				    #attend relachement BP2
        #print(Rpi_IO.input(BP))
        i+=1
        if i==1:
            print( "phase 1")
            phase=1
            Rpi_IO.output(LEDG,1)                
        if i==15:
            print( "phase 2")
            phase=2
            Rpi_IO.output(LEDG,0)
        if i==40:
            print ("phase 3")
            phase=3
            Rpi_IO.output(LEDB,1)
        if i==60:
            print( "phase 4")
            phase=4
            Rpi_IO.output(LEDB,0)
        if i==90:
            print( "phase 5")
            phase=5
            Rpi_IO.output(LEDR,1)

        time.sleep(0.1)	
    
    Rpi_IO.output(LEDR,0)
    Rpi_IO.output(LEDG,0)
    Rpi_IO.output(LEDB,0)

    if phase==1:
        print( "phase 1")
        if Rpi_IO.input(screen):
            Rpi_IO.output(screen,0)
            shared.set('serverOperation', "screenOff")
        else:
            Rpi_IO.output(screen,1)
            shared.set('serverOperation', "screenOn")
    elif phase==2:
        print( "phase 2")
    elif phase==3:
        os.system("python3 "+directory +"/action.py --action 'music_stop' &")
        time.sleep(3)
        os.system(directory +"/../loadAya.sh")
    elif phase==5:
        os.system("sudo reboot")

        
#configuration des evenement lies au bouton poussoir (gestion INT et anti rebond)
Rpi_IO.add_event_detect(BpGpio,Rpi_IO.RISING,Appui_BP,200)		

#****************************************************************************************************************



def start_keyphrase_recognition(keyphrase_function, key_phrase):


    modeldir = directory

    # Create a decoder with certain model
    config = pocketsphinx.Decoder.default_config()
    # Use the mobile voice model (en-us-ptm) for performance constrained systems

    config.set_string('-hmm', os.path.join(directory,'pocketsphinx/en-us/en-us-ptm'))
    config.set_string('-dict', os.path.join(directory,'pocketsphinx/en-us/cmudict-en-us.dict'))

    #config.set_string('-hmm', os.path.join(modeldir, 'pocketsphinx/fr-FR/fr-FR-ptm'))
    #config.set_string('-dict', os.path.join(modeldir, 'pocketsphinx/fr-FR/cmudict-fr-FR.dict'))
    config.set_string('-keyphrase', key_phrase)

    #config.set_string('-logfn', directory+'/pocketsphinx/sphinx.log')
    config.set_float('-kws_threshold', 1)

    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=1024)
    stream.start_stream()

    decoder = pocketsphinx.Decoder(config)
    decoder.start_utt()
    print("ready")
    while True:
        buf = stream.read(1024)
        if buf:
            decoder.process_raw(buf, False, False)
        else:
            break
        if decoder.hyp() is not None:
            keyphrase_function()
            decoder.end_utt()
            decoder.start_utt()


def keyWordDetected():
    print("--------------------Keyword detected!")
    shared.set('keyWordDetect', 1)
    Rpi_IO.output(LEDG,1)
    


if __name__ == "__main__":
    start_keyphrase_recognition(keyWordDetected, keyWord)
