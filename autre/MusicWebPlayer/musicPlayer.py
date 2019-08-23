#!/usr/bin/env python
# -*- coding: utf-8 -*-

import cherrypy
from cherrypy import tools
import os
from cherrypy.lib.static import serve_file

from urllib.parse import quote, unquote
from eyed3 import id3

initial_directory="/home/pi/Music/"
path   = os.path.abspath(os.path.dirname(__file__))

class Download:

    @cherrypy.expose
    def index(self):
      return serve_file(os.path.join(path, 'assistantPlayer.html')) 

    @cherrypy.expose
    def musicPlayer_liste(self, **params):
      
      response=""
      #try:
      
      recherche=""
      if "recherche" in params:
        recherche=params["recherche"]

      if "directories" in params:
        files=os.listdir(initial_directory)

        for file in files:  
          if(os.path.splitext(file)[1]=="") and (recherche in file or recherche==""):
            response+="""<li class="mv-item"><a onclick="afficher_music_file('"""+quote(file)+"""')">"""+file+"""</a></li>"""
        return response

      else:
        if "dossier" in params:
          #url decode
          dossier=unquote(params["dossier"])
          directory=initial_directory+dossier


          titreDir=os.path.basename(dossier)
          precDir=os.path.dirname(dossier)

          if titreDir!='':
            response+="""<div id="titre_pages"><img onclick="afficher_music_file('"""+quote(precDir)+"""')" height="40px" src="https://sjtm.fr/domotix/img/cloud/precedent.png" style="float:left; cursor:pointer; padding-top:5px;">"""+titreDir+"""</div></div><br><br>"""
          else:
            response+='<div id="titre_pages">'+"Musiques"+'</div><br><br>'

        else:
          dossier=''
          directory=initial_directory
          response+='<div id="titre_pages">Toutes les Musiques</div>'


        files=os.listdir(directory)

        nbFiles=0
        dirList = []
        musicList = []

        for file in files:  
          if(os.path.splitext(file)[1]=="") and (recherche in file or recherche==""):
            dirList.append(file)
          if(os.path.splitext(file)[1]==".mp3" or os.path.splitext(file)[1]==".ma4" or os.path.splitext(file)[1]==".wma") and (recherche in file or recherche==""):
            musicList.append(file)
            nbFiles+=1


        if dossier=='':
          for file in dirList:
            files=os.listdir(initial_directory+file)
            for file2 in files:
              if(os.path.splitext(file2)[1]==".mp3" or os.path.splitext(file2)[1]==".ma4") and (recherche in file2 or recherche==""):
                musicList.append(file+'/'+file2)
                nbFiles+=1 

        else:   
          if len(dirList) > 0:
            response+='<div class="music_header_title">Dossiers</div>'
            for file in dirList:  
              response+="""<div class="folder_title" title='"""+file+"""' onclick="afficher_music_file('"""+quote(dossier+'/'+file)+"""')">"""+file+"""</div>"""

        if len(musicList) > 0:
          response+='<br><br><div class="nb_playlist"><?php echo $nb_fichier;?>'+str(nbFiles)+' Musique'
          if nbFiles > 1: 
            response+='s</div>'
          else:
            response+='</div>'

          response+='<div class="music_header_title">Title</div>'
          i=0
          for file in musicList:  
            response+="""<div class="music_title" id="'"""+str(i)+"""'" name='"""+quote(dossier+'/'+file)+"""' onclick="play_music( this.getAttribute('name'),this.innerHTML,this.id)" title='"""+os.path.splitext(file)[0]+"""'>"""+os.path.splitext(file)[0]+"""</div>"""
            i+=1

        response+='<div style="height:150px; width:100%;"></div>'
        return response




    @cherrypy.expose
    #@cherrypy.tools.json_in()
    #@cherrypy.tools.json_out()
    def getTag(self, **params):
      
      
      """file = str(unquote(file))
      file = "/musiques 22/06 My Name Is Stain.mp3"
      tag = id3.Tag()
      tag.parse(initial_directory+file)
      
      return	'{"result":"yes","titre":"'+quote(tag.title)+'","artist":"'+quote(tag.artist)+'","year":"","album":"'+quote(tag.album)+'","genre":"","time":"","image":""}'
      """
      return 	'{"result":"yes","titre":"","artist":"","year":"","album":"","genre":"","time":"","image":""}'
      """
      if "file" in params:  
         
        return 	'{"result":"yes","titre":"qsdqsd","artist":"qsdqsd","year":"","album":"","genre":"","time":"","image":""}'

      else:
        return 	'{"result":"yes","titre":"","artist":"","year":"","album":"","genre":"","time":"","image":""}'
      """

    @cherrypy.expose
    def player(self, **params):

      if "file" in params:   
        file = str(unquote(params["file"]))   #.replace("'", "\'")     #.replace("(", "\(") .replace(")", "\)") .replace("-", "\\-")   
        return serve_file( initial_directory+file, "application/x-download", "attachment")



config = {
  'global' : {
    'tools.response_headers.on': True,
    'server.socket_host' : '0.0.0.0',
    'server.socket_port' : 8087,
  }
}


if __name__ == '__main__':
    cherrypy.quickstart(Download(),'/',config)