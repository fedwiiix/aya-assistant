#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse, memcache


parser = argparse.ArgumentParser()                                                   
parser.add_argument("-a", "--action", default='',  help="action for assistant -> actions: play, pause, stop, next, previous / volume: v[0:200] / mode: random, standard")
parser.add_argument("-f", "--file", default='',  help="choose file")

args = parser.parse_args()

if args.action:
	print(args.action)
	shared = memcache.Client(['127.0.0.1:11211'], debug=0)
	shared.set('musicPlayerCmd', args.action)
elif args.file:
	print(args.file)
	shared = memcache.Client(['127.0.0.1:11211'], debug=0)
	shared.set('musicPlayerCmd', "file"+args.file)

else:

	import vlc,time, configparser, urllib.parse, random, os
	from requests.auth import HTTPDigestAuth
	import requests, json
	headers = {'User-Agent': 'Mozilla/5.0 Chrome/39.0.2171.95 Safari/537.36'}
	import RPi.GPIO as Rpi_IO

	LEDB = 26    #B
	Rpi_IO.setmode(Rpi_IO.BCM)	   			            
	Rpi_IO.setwarnings(False)		            
	Rpi_IO.setup(LEDB,Rpi_IO.OUT)	
	Rpi_IO.output(LEDB,1)


	directory= os.path.dirname(__file__)                                                # get directory
	if directory=='':
		directory= os.getcwd()

	Config = configparser.ConfigParser()
	Config.read(directory+"/config.ini")
	musicPlayerPass = Config["musicPlayer"]['musicPlayerPass']	
	musicDirectory = Config["musicPlayer"]['musicDirectory']	
	localMusicdirectory = Config["musicPlayer"]['localMusicdirectory']	
	volume = int(Config["musicPlayer"]['volume'])
	if volume<50:
		volume=50

	webServerAdress = Config["webServer"]['webServerAdress']
	auth=HTTPDigestAuth(Config["webServer"]['user'], Config["webServer"]['pass'])

	previousMusic = []
	dirList = []
	playlist = []
	idSong=0

	vlc_instance = vlc.Instance()
	player = vlc_instance.media_player_new()
	player.audio_set_volume(volume)

	mode="random"
	play=1
	limitTry=10

	def getPlaylist(file):
		try:
			r = requests.get(webServerAdress+"musicPlayer/playerApi.php?action=getListMusic&path="+urllib.parse.quote_plus(file) , auth=auth, headers=headers)
			playlist = json.loads((r.content).decode("utf-8"))
			#print(playlist)
			idSong = random.randint(1, len(playlist)-1)
			return playlist, idSong
		except:
			return [], 0

	def getListDir(file,display):
		try:
			r = requests.get(webServerAdress+"musicPlayer/playerApi.php?action=getListDir&path="+urllib.parse.quote_plus(file), auth=auth, headers=headers)
			dirList = json.loads((r.content).decode("utf-8"))
			#print(dirList)
			if display==1:
				text=""
				i=1
				for x in dirList:
					text+=str(i) +" - "+ x +"<br>"
					i+=1
				if text=="":
					text="Aucune playlist trouvé"
				screenDisplay('{"type":"text","text":"'+text+'","timeout":"none"}')
			return dirList
		except:
			return []

	def getCmd():
		shared = memcache.Client(['127.0.0.1:11211'], debug=0)
		cmd = shared.get('musicPlayerCmd')
		if cmd!="wait":
			shared.set('musicPlayerCmd', "wait")
			print(cmd)
		return cmd

	def set_log(text):
		now = time.strftime('%H:%M %d-%m-%Y', time.localtime())
		file = open(directory+'/log/aya.log','a')
		file.write(now +" -> "+  text+'<br>\n')
		print(" -> "+ text) # now +
		file.close()

	def screenDisplay(text):
		#print(text)
		shared = memcache.Client(['127.0.0.1:11211'], debug=0)
		shared.set('serverOperation', text)


	playlist, idSong = getPlaylist(musicDirectory)
	dirList = getListDir("",0)
	inactiveDelay=0
	
	Rpi_IO.output(LEDB,0)
	shared = memcache.Client(['127.0.0.1:11211'], debug=0)
	cmd = shared.get('musicPlayerCmd')	# if 2 are load in same time
	if cmd=="wait":
		print("already run")
		set_log("serveur de musique deja en route")
		exit(0)
	shared.set('musicPlayerCmd', "play")
	

	while True:

		cmd = getCmd()
		if cmd != "wait":
			cmd=cmd.lower()
			inactiveDelay=0
			if cmd=="play":
				playlist, idSong = getPlaylist(musicDirectory)
				play=1

			if len(cmd)>3 and cmd[:4]=="file":
				if len(cmd[4:])<3 and int(cmd[4:])<=len(dirList) and int(cmd[4:])>0 :
					musicDirectory=dirList[int(cmd[4:])-1]
				elif cmd[4:] in dirList:
					musicDirectory=cmd[4:]
				playlist, idSong = getPlaylist(musicDirectory)
				play=1
		
		inactiveDelay+=1
		if inactiveDelay>900:	# exit after 30 min delay
			player.stop()
			shared = memcache.Client(['127.0.0.1:11211'], debug=0)
			shared.set('musicPlayerCmd', "")
			Config.set('musicPlayer', 'musicDirectory', musicDirectory)			# sve volume and initial directory
			Config.set('musicPlayer', 'volume', str(volume))
			with open(directory+"/config.ini", 'w') as configfile:
				Config.write(configfile)
			exit(0)
		
		set_log("Demarage du serveur de musique")
		while play:
			try:
				#print(playlist)
				if len(playlist)<2:
					print("no music")
					play=0
					break

				while playlist[idSong]=="":
					if mode=="random":
						idSong = random.randint(1, len(playlist)-1)
					else:
						idSong+=1
						if len(playlist)==idSong:
							break

				previousMusic.append(playlist[idSong])
				
				song = localMusicdirectory+"/"+musicDirectory+"/"+playlist[idSong]
				if os.path.isfile(song)==False:
					print("no local file")
					song = webServerAdress+"musicPlayer/player.php?pass="+musicPlayerPass+"&file="+urllib.parse.quote_plus(musicDirectory+"/"+playlist[idSong])
				
				print("load:",playlist[idSong])
				playlist.remove(playlist[idSong])

				

				media  = vlc_instance.media_new(song)
				player.set_media(media)
				player.play()
				
				time.sleep(1.5)
				while str(player.get_state()) == "State.Opening":
					time.sleep(1) # startup time.

				limitTry=20	
				#duration = player.get_length() / 1000
				#mm, ss   = divmod(duration, 60)
				#print ("Length:", "%02d:%02d" % (mm,ss))

				'''media.parse() 							# Synchronous parse stream and get meta
				meta = vlc.Meta()
				info = media.get_meta(meta) 
				print(info)'''

				while str(player.get_state()) == "State.Playing" or str(player.get_state()) == "State.Paused":
				
					cmd = getCmd()
					if cmd != "wait":
						cmd=cmd.lower()
						inactiveDelay=0
						if cmd == "pause":
							player.pause()
						elif cmd == "play":
							player.play()
						elif cmd == "stop":
							player.stop()
							shared = memcache.Client(['127.0.0.1:11211'], debug=0)
							shared.set('musicPlayerCmd', "")
							Config.set('musicPlayer', 'musicDirectory', musicDirectory)			# sve volume and initial directory
							Config.set('musicPlayer', 'volume', str(volume))
							with open(directory+"/config.ini", 'w') as configfile:
								Config.write(configfile)
							exit(0)

						elif cmd == "next":
							player.stop()

						elif cmd == "previous":
							mm, ss   = divmod(player.get_time() / 1000, 60)
							#print ("Length:", "%02d:%02d" % (mm,ss))
							prev=len(previousMusic)
							if prev > 0 and ss>10:
								playlist[idSong]=previousMusic[prev-1]
								del previousMusic[-1]
								player.stop()
							elif prev > 1 and ss<10:
								playlist[idSong]=previousMusic[prev-2]
								del previousMusic[-1]
								del previousMusic[-1]
								player.stop()
							
						elif len(cmd)>0 and cmd[0]=="v":
							volume=int(cmd[1:])
							if volume < 110:
								player.audio_set_volume(volume)

						elif cmd=="increasevolume" and volume<150:
							volume+=5
							player.audio_set_volume(volume)
						elif cmd=="decreasevolume" and volume>0:
							volume-=5
							player.audio_set_volume(volume)
						elif cmd=="increase" and volume<150:
							player.audio_set_volume(volume)
						elif cmd=="decrease" and volume>50:
							player.audio_set_volume(40)
						
						elif cmd=="displayplaylist":
							dirList = getListDir("",1)
							
						elif cmd =="random" or cmd=="standard":
							mode=cmd

						if len(cmd)>3 and cmd[:4]=="file":
							if len(cmd[4:])<3 and int(cmd[4:])<=len(dirList) and int(cmd[4:])>0 :
								musicDirectory=dirList[int(cmd[4:])-1]
							elif cmd[4:] in dirList:
								musicDirectory=cmd[4:]
							playlist, idSong = getPlaylist(musicDirectory)
							break

						else:
							pass
						
					time.sleep(1) # if 1, then delay is 1 second.

			except Exception as e:
				set_log('<b style="color:red">musicPlayer error:</b> '+ str(e))
				time.sleep(1)
				limitTry-=1
				if limitTry<0:
					exit(1)

		time.sleep(2)