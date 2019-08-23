#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import aiy.audio
import logging
import aiy.assistant.grpc
import aiy.voicehat
aiy.i18n.set_language_code('fr-FR')
logging.basicConfig( level=logging.INFO, format="[%(asctime)s] %(levelname)s:%(name)s:%(message)s" )
from weather import Weather, Unit
from geotext import GeoText
import time, datetime
from py_translator import Translator
import configparser
import subprocess
from pygame import mixer
import RPi.GPIO as Rpi_IO
import memcache
import requests, json, random, os,sys
from requests.auth import HTTPDigestAuth




directory= os.path.dirname(__file__)                                                # get directory
if directory=='':
    directory= os.getcwd()

Config = configparser.ConfigParser()
Config.read(directory+"/../config.ini")
action_dir = 'python3 '+ directory+"/../action.py --action "
temperature_BMP280_cmd = "python2.7 "+directory+"/../api/BMP280.py"
temperature_DHT22_cmd = "python2.7 "+directory+"/../api/DHT22.py"

webserveradress = Config["webServer"]['webserveradress']	
headers = {'User-Agent': 'Mozilla/5.0 Chrome/39.0.2171.95 Safari/537.36'}
authVal=HTTPDigestAuth(Config["webServer"]['user'], Config["webServer"]['pass'])


assistant = aiy.assistant.grpc.get_assistant()

#   ================================================ definition des commandes

meteo = ["Cloudy","Mostly Cloudy","Partly Cloudy","Rain","Showers","Scattered Showers","Breezy","Clear", "Sunny","Windy","Snow Showers","Thunderstorms","Scattered Thunderstorms"]
meteo_traduite = ["Nuageux", "Plutôt nuageux", "Partiellement nuageux", "Pluvieux", "Pluvieux", "parsemé d'averses", "Frais", "Clair", "Ensoleillé", "Venteux", "Averses de neige", "Orages", "Orages éparpillées"]
days = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday","today", "tomorow"]
jour = ['lundi','mardi','mercredi','jeudi','vendredi','samedi','dimanche']
mois = ['janvier','février','mars','avril','mai','juin','juillet','aout','septembre','octobre','novembre','décembre']

global reponse_active
reponse_active = '1'

conversation_json = json.load( open(directory + '/conversation.json') )

#   ================================================================================================ little fonctions

def test_mot_cle(text, words):

    for oneWord in words:
        if oneWord.lower() not in text:
            return False
    return True 

def translate_word(word):
    translate = translator.translate(word, dest='fr')                    
    return translate.text

def reponse_speak(text):
    global reponse_active
    print(text)
    if reponse_active == '1':
        aiy.audio.say(text)

def set_log(text):
    now = time.strftime('%H:%M %d-%m-%Y', time.localtime())
    file = open(directory+'/../log/aya.log','a')
    file.write(now +" -> "+  text+'<br>\n')
    print(" -> "+ text) # now +
    file.close()

def screenDisplay(text):
    shared = memcache.Client(['127.0.0.1:11211'], debug=0)
    shared.set('serverOperation', text)

#   ================================================================================================ conversation and command

def get_conversation_reponse(text):
    reponse=""

    for x in conversation_json['question']:

        if x['question'].lower() == text:

            if 'nb_rep' in x:
                rand = random.randrange(int(x['nb_rep']))+1
                reponse = x[str(rand)]
                reponse_speak(reponse)
                break

    for x in conversation_json['commandes']:
        for y in x['keyword']:
            
            if test_mot_cle(text, y):

                if 'action' in x:
                    reponse=""
                    if 'reponse' in x:
                        reponse = x['reponse'][random.randrange(len(x['reponse']))]

                    if x['action'] == 'os':
                        os.system(x['cmd'])    
                         
                    elif x['action'] == 'action_domotix':
                        if x['cmd']=="playlist":
                            text = text.split('playlist ')
                            if str(text[1]) != '':
                                os.system(action_dir +"'music_playlist_"+str(text[1]).lstrip('numéro ')+"' &")
                        else:
                            os.system(action_dir + x['cmd']+" &")   
                    elif x['action'] == 'volume':
                        vol = ''.join(i for i in text if i.isdigit())
                        os.system(action_dir + "music_v"+vol+" &")
                        
                    elif x['action'] == 'reponse_active':
                        global reponse_active
                        reponse_active = x['cmd']

                    elif x['action'] == 'heure':
                        tmp=time.strftime('%H:%M', time.localtime()) 
                        reponse += tmp
                        screenDisplay('{"type":"text","text":"Heure: '+tmp+'"}')

                    elif x['action'] == 'day' or x['action'] == 'date':   
                        reponse = date(x['action']) 

                    elif x['action'] == 'temperature':
                        tmp=get_BMP280("temperature")+" degrés"
                        reponse += tmp.replace(".", ",")
                        screenDisplay('{"type":"text","text":"Temperature: '+tmp+'"}')

                    elif x['action'] == 'humidite':
                        tmp=get_DHT22("humidite")+" %"
                        reponse += tmp.replace(".", ",")
                        screenDisplay('{"type":"text","text":"humidité: '+tmp+'"}')
                    
                    elif x['action'] == 'presure':
                        tmp = get_BMP280("presure")+" pascales"
                        reponse += tmp.replace(".", ",")
                        screenDisplay('{"type":"text","text":"Pression: '+tmp+'"}')

                    elif x['action'] == 'agenda':
                        reponse += get_agenda(text)
                    
                    elif x['action'] == 'alarme':
                        reponse += set_alarme(text)
                    
                    elif x['action'] == 'citation':
                        reponse += get_citation(text)

                    elif x['action'] == "meteo":
                        reponse += weather(text)

                    elif x['action'] == 'affiche':
                        if x['lien'] and x['lien'][:4]=="http" and x['lien']!="":
                            screenDisplay('{"type":"link","text":"'+x['lien']+'"}')
                        elif x['lien']:
                            screenDisplay('{"type":"link","text":"'+webserveradress+x['lien']+'"}')
                            
                        
                    
                    reponse_speak(reponse)
                break

#   ================================================================================================ check the devices

def get_citation():
    
    r = requests.get(webserveradress+"database/getDbApi.php?request=random_citation", auth=authVal, headers=headers)
    try:
        decoded = json.loads((r.content).decode("utf-8"))

        # Access data
        for x in decoded['citation']:
            reponse = x['citation']
            if x['auteur'] != '':
                reponse += '... Citation de '+x['auteur']
        return reponse

    except (ValueError, KeyError, TypeError):
         print("JSON format error get_citation")

#   ================================================================================================ get database

def get_database():
    r = requests.get(webserveradress+"database/getDbApi.php?request=all_tables", auth=authVal, headers=headers)

    #print(r.text)

    decoded = json.loads((r.content).decode("utf-8"))

    global assistant_name
    global sms_link
    global piece
    global city
    global pieces

    for x in decoded['parametres']:
        if x['id'] == 'assistant':
            assistant_name = x['parametre']
        if x['id'] == 'lien_sms':
            sms_link = x['parametre']
        if x['id'] == 'piece':
            piece = x['parametre']
        if x['id'] == 'ville':
            city = x['parametre']

    for x in decoded['appareils']:
        code = x['code_radio'].split('/')

        print(x['mode'])

        bouton = x['nom_bouton'].split('/')

        if len(code)<3:
            code2 = code[0]
            if len(code)==2:
                code2 = code[1]
            if x['piece']==piece:
                x['piece']=""

            bouton2 = "off"
            if len(bouton)==2:
                bouton2 = bouton[1]
            conversation_json['commandes'].append( { "keyword":[["allume", x['nom'], x['piece'] ],["met", x['nom'], x['piece'], bouton[0] ]], "action": "action_domotix", "cmd":"'"+x['mode']+"' -c '"+code[0]+"'", "reponse": ["je l\'allume", x['nom']+" allumé", ""] } )
            conversation_json['commandes'].append( { "keyword":[["étein", x['nom'], x['piece'] ],["met", x['nom'], x['piece'], bouton2 ]], "action": "action_domotix", "cmd":"'"+x['mode']+"' -c '"+code2+"'", "reponse": ["je l'éteind", x['nom']+" éteind", ""]} )
        else:
            for i in range(0, len(code)):
                conversation_json['commandes'].append({ "keyword": [["allume", x['nom'], x['piece'], bouton[i] ],["met", x['nom'], x['piece'], bouton[i] ],["demarre", x['nom'], x['piece'], bouton[i] ]], "action": "action_domotix", "cmd":"'"+x['mode']+"' -c '"+code[i]+"'", "reponse": ["Bien reçu", x['nom']+" sur "+bouton[i], ""] })


    

    print("Mise en marche de "+assistant_name)

#   ================================================================================================ date

def date(mode):

    tim = time.localtime().tm_wday    # on cherche le jour de la semaine
    reponse = jour[int(tim)]
    if mode == 'date':
        tim = time.strftime('%d', time.localtime())
        if tim[0] == '0':
            reponse += ' '+tim[1]+' '  
        else:
            reponse += ' '+tim+' '  

        tim = time.localtime().tm_mon
        reponse += mois[int(tim)-1]   
    return reponse

#   ================================================================================================ weather

def get_BMP280(mode):

    try:
        process = subprocess.Popen(temperature_BMP280_cmd, stdout=subprocess.PIPE,stderr=subprocess.PIPE, shell=True)                 
        (output, err) = process.communicate()                                               # load netdiag and get output json diag info
        process.wait()
        print('stdout:',output)
        decoded = json.loads(output.decode("utf-8"))
        if mode=="temperature":
            return decoded['Temperature']
        else:
            return decoded['Pressure']
    except:
        pass

def get_DHT22(mode):

    try:
        process = subprocess.Popen(temperature_DHT22_cmd, stdout=subprocess.PIPE,stderr=subprocess.PIPE, shell=True)                 
        (output, err) = process.communicate()                                               # load netdiag and get output json diag info
        process.wait()
        print('stdout:',output)
        decoded = json.loads(output.decode("utf-8"))
        if mode=="temperature":
            return decoded['Temperature']
        else:
            return decoded['Humidity']
    except:
        pass

def weather(text):

    weather = Weather(unit=Unit.CELSIUS)
    #lookup = weather.lookup(560743)
    #condition = lookup.condition
   
    reponse=""
    places = GeoText(text)
    if places.cities:
        #print(places.cities[0])
        location = weather.lookup_by_location(places.cities[0])
        reponse="A "+places.cities[0]+", "
    else:
        global city
        location = weather.lookup_by_location(city)
    condition = location.condition

    date = time.localtime().tm_wday
    day = days[int(date)]

    i=0
    for oneWord in days:
        if oneWord.lower() in text:
            if oneWord.lower() == "tomorow":
                if day == "sunday":
                    date=0
                    print("monday")   
                else:
                    date+=1
                    print(days[date])   
            elif oneWord.lower() != "today":
                date = i
                #print(oneWord)   
        i+=1 

    forecasts = location.forecast
    for forecast in forecasts:
        
        dt = datetime.datetime.strptime( str(forecast.date), '%d %b %Y').date()      # get day
        dt = dt.weekday()

        if date == dt:
            print(forecast.date)

            text_temps = forecast.text
            for x in range(0,13):

                if text_temps == meteo[x]:
                    reponse += "Le temps sera "+meteo_traduite[x]
                    pass

                temp_high = str(forecast.high)
                temp_low = str(forecast.low)
                temp_high = temp_high.replace(".", ",")
                temp_low = temp_low.replace(".", ",")

            rand = random.randint(0, 2)
            if rand == 0:
                reponse += ". Les maximales seront de "+temp_high+" degrés et les minimales de "+temp_low+" degrés."
            elif rand == 1:
                reponse += ". La température variera entre "+temp_low+" et "+temp_high+" degrés."
            else: 
                reponse += ". La température vas varier entre "+temp_low+" et "+temp_high+" degrés."
            
            print(reponse)
            return reponse
            break

#   ================================================================================================ agenda

def get_agenda(text):
    periode = ["aujourd'hui",'demain','weekend','semaine']
    periodeMode = ['today','tomorrow','weekend','week']

    mode='today'
    i=0
    for oneWord in periode:
        if oneWord in text:
            mode=periodeMode[i]
            break
        i+=1
    r = requests.get(webserveradress+"database/getDbApi.php?request=agenda&mode="+mode, auth=authVal, headers=headers)
    try:
        decoded = json.loads((r.content).decode("utf-8"))
       
        reponse = "Vous avez "+str(len(decoded['agenda']))+" évenements"
        prec_day = -1
        reponse = ''

        if len(decoded['agenda']) != 0:
            for x in decoded['agenda']:

                date_event = x['date_event'].split('-')
                year_now = datetime.datetime.now()

                if year_now.year == int(date_event[0]) or year_now.year == (int(date_event[0])+1):
                    year_now = int(date_event[0])
                else:
                    year_now = year_now.year
                
                tim = datetime.datetime( year_now, int(date_event[1]), int(date_event[2]), 15, 54, 12, 14418)   # on cherche le jour de la semaine
                jour_now = time.localtime().tm_wday    # on cherche le jour de la semaine

                if prec_day != tim.weekday():
                    prec_day = tim.weekday()
                    if int(jour_now) == int(tim.weekday()) and mode!= 'tomorrow':
                        reponse += ". aujourd'hui"
                    else:
                        reponse += '. '+jour[int(tim.weekday())]

                if x['type_agenda'] == 'Agenda': 
                    reponse += ', vous avez: '+x['event']

                elif x['type_agenda'] == 'Anniversaire':
                    reponse += ", vous avez l'anniversaire de "+x['event']
        else:
            if mode=='today':
                reponse= "Vous n'avez rien de prévu aujourd'hui"
            elif mode=='tomorrow':
                reponse= "Vous n'avez rien de prévu demain"
            elif mode=='week':
                reponse= "Vous n'avez rien de prévu cette semaine"
            elif mode=='weekend':
                reponse= "Vous n'avez rien de prévu ce weekend"
        
        return reponse

    except:
        pass

#   ================================================================================================ agenda

def set_alarme(text):
    
    h = time.localtime().tm_hour
    m = time.localtime().tm_min

    
    return ""

#   ================================================================================================ variables
#   ================================================================================================

#get_playlist()
result_db = get_database()

