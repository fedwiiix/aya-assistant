#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from assistantFunctions.assistantFunctions import *

#   ================================================================================================
#   ================================================================================================

mixer.init()
mixer.music.load(directory+'/sound/ok.mp3')
mixer.music.play()

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
BpGpio = 23    										# gpio bp											
#Rpi_IO.setup(BpGpio,Rpi_IO.IN,Rpi_IO.PUD_UP)		#configuration broches en entree routine d'interruption
Rpi_IO.setup(BpGpio,Rpi_IO.IN) #,Rpi_IO.PUD_UP)		#configuration broches en entree routine d'interruption
def Appui_BP (BP):								    # si le bp est presser

    shared = memcache.Client(['127.0.0.1:11211'], debug=0)  
    i=0
    phase=0
    if shared.get('keyWordDetect')==0:
        
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
            if i==80:
                print( "phase 5")
                phase=5
                Rpi_IO.output(LEDR,1)
            if i==100:
                print( "phase 6")
                phase=6

            time.sleep(0.1)	

        Rpi_IO.output(LEDR,0)
        Rpi_IO.output(LEDG,0)
        Rpi_IO.output(LEDB,0)

        if phase==1:
            print( "phase 1")
            shared.set('keyWordDetect', 1) 
            Rpi_IO.output(screen,1)
        elif phase==2:
            print( "phase 2")
        elif phase==3:
            os.system("python3 "+directory +"/../action.py --action kill &")
        elif phase==5:
            os.system("sudo halt")


#configuration des evenement lies au bouton poussoir (gestion INT et anti rebond)
Rpi_IO.add_event_detect(BpGpio,Rpi_IO.RISING,Appui_BP,200)		
Rpi_IO.output(LEDG,1)


''' #------------------------------------------
	#--------- PROGRAMME PRINCIPAL ------------
	#------------------------------------------'''

def main():

    shared = memcache.Client(['127.0.0.1:11211'], debug=0)  
    limitTry=100
    musicPlayerReduce=0

    set_log("Lancement de Aya")
    with aiy.audio.get_recorder():
        while True:
            try:

                if musicPlayerReduce==1:
                    shared.set('musicPlayerCmd', "increase")
                    musicPlayerReduce=0 

                shared.set('keyWordDetect', 0) 
                Rpi_IO.output(LEDG,0)
                print('Press the button and speak')

                now=time.localtime(time.time()).tm_min
                while shared.get('keyWordDetect')==0:
                    if now!=-1 and time.localtime(time.time()).tm_min == now+5 or time.localtime(time.time()).tm_min == now-60+5:
                        Rpi_IO.output(screen,0)
                        shared.set('serverOperation', "screenOff")
                        now=-1
                    time.sleep(0.2)      

                cmd = shared.get('musicPlayerCmd')
                if cmd=="wait":
                    shared.set('musicPlayerCmd', "decrease")
                    musicPlayerReduce=1                  
                
                mixer.music.play()
                Rpi_IO.output(LEDG,1)

                print('Listening...')
                text, audio = assistant.recognize()
                if text is not None:
                    mixer.music.play()
                    screenDisplay('{"type":"text","text":"'+text+'","timeout":"1500"}')
                    text = text.lower()


                    if "sms" in text:
                        msg = text.split('sms')
                        if str(msg[1]) != '':
                            screenDisplay('{"type":"text","text":"Message: '+str(msg[1])+'"}')
                            reponse_speak("Message: "+str(msg[1])+". Validez vous?")
                            print('Listening...')
                            text, audio = assistant.recognize()
                            if text is not None and 'oui' in text or 'valide' in text:
                                try:
                                    global sms_link, assistant_name
                                    requests.get( str(sms_link) + assistant_name+': '+ str(msg[1]))
                                    screenDisplay('{"type":"text","text":"SMS envoyé: '+str(msg[1])+'"}')
                                    reponse_speak("SMS envoyé")
                                except Exception as e:
                                    set_log('<b style="color:red">error:</b> '+ str(e))
                                    reponse_speak("le SMS n'a pas été envoyé")
                                    pass

                    elif "traduire" in text:
                        trad = text.split('traduire')
                        if str(trad[1]) != '':
                            reponse = Translator().translate(text=str(trad[1]), dest='fr').text
                            reponse_speak('La traduction de: ')
                            aiy.audio.say(str(trad[1]), lang='en-GB')
                            print('Translate: '+reponse)
                            screenDisplay('{"type":"text","text":"La traduction de: '+str(trad[1])+' est: '+reponse+'"}')
                            reponse_speak(' est: '+reponse)
                                                    
                    else:
                        get_conversation_reponse(text)
                        
                        if text == 'éteins-toi':
                            reponse_speak("êtes vous sûre de vouloir m'éteindre?")
                            text, audio = assistant.recognize()
                            if text is not None and 'oui' in text or 'valide' in text or 'je suis sûr' in text:
                                reponse_speak("au revoir")
                                os.system("python3 "+directory +"/../action.py --action kill &")

                    set_log(text)
                   
                if audio is not None:
                    #print('Unkown')
                    pass

                enableVoice=0

            except Exception as e:
                Rpi_IO.output(LEDG,0)
                Rpi_IO.output(LEDB,1)
                Rpi_IO.output(LEDR,1)
                set_log('<b style="color:red">error:</b> '+ str(e))
                time.sleep(1)
                limitTry-=1
                enableVoice=0
                Rpi_IO.output(LEDR,0)
                Rpi_IO.output(LEDB,0)
                if limitTry<0:
                    exit(1)

#   ================================================================================================
#   ================================================================================================

if __name__ == "__main__":

    main()
