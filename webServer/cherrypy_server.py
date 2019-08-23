#! /usr/bin/python3.5
# -*- coding:utf-8 -*-

import cherrypy
from cherrypy.lib import auth_basic
from cherrypy.lib.static import serve_file
import configparser
import os
import memcache
shared = memcache.Client(['127.0.0.1:11211'], debug=0)
text = shared.set('serverOperation', '')

directory= os.path.dirname(__file__)                                                # get directory
if directory=='':
    directory= os.getcwd()

Config = configparser.ConfigParser()
Config.read(directory+"/../config.ini")
pass_capture = Config["cherrypy"]['pass_capture']			
pass_action = Config["cherrypy"]['pass_action']
pass_webApp = Config["cherrypy"]['pass_webApp']

user = Config["cherrypy"]['user']
password = Config["cherrypy"]['password']

USERS = { user: password } 
path   = os.path.abspath(os.path.dirname(__file__))

"""def index(self, **params):
        try:
            if 'pass' in params and params["pass"] == pass_webApp:
                return serve_file(os.path.join(path, 'index.html')) 
            return pass_webApp
        except:
            cherrypy.log(" -> Connection failed")
"""

class font_end(object):

    shared = memcache.Client(['127.0.0.1:11211'], debug=0)
    screen="5000"
        
    @cherrypy.expose
    def index(self):
        return serve_file(os.path.join(path, 'index.html')) 

    @cherrypy.expose
    def getUpdate(self):
        cherrypy.response.headers["Content-Type"] = "text/event-stream;charset=utf-8"
        text = self.shared.get('serverOperation')
        
        if text!="":
            self.shared.set('serverOperation', '')
            if text == "screenOn" and self.screen=="5000":
                self.screen="1000"
                return 'retry: '+self.screen+'\ndata: {"type":"refresh","mode":1} \n\n'
            elif text == "screenOff" and self.screen=="1000":
                self.screen="5000"
                return 'retry: '+self.screen+'\ndata: {"type":"refresh","mode":0} \n\n'
            
            return 'retry: '+self.screen+'\ndata: ' + text + '\n\n'
                
        else:
            pass #return 'retry: 200\ndata: {"type":""} \n\n'


    @cherrypy.expose
    def resetTxt(self):
        
        text = self.shared.get('serverOperation')
        if text!="" and text!="screenOn" and text!="screenOff":
            self.shared.set('serverOperation', '')
            return text
        elif text=="screenOn" or text=="screenOff":
            self.shared.set('serverOperation', '')
            return text

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def action_domotix(self, **params):
        try:
            if 'pass' in params and params["pass"] == pass_action:
                action = params["action"].replace("%20", " ")
                if 'mode' in params and params["mode"]:
                    mode = params["mode"].replace("%20", "")
                    os.system("python3 "+directory+"/../action.py --action '"+mode+"' -c '"+action+"'")
                else:
                    os.system("python3 "+directory+"/../action.py --action '"+action+"'")
                print("action: "+action)
                cherrypy.log(" -> action:",action) 
                return { 
                    'action' :  action
                    }
        except:
            cherrypy.log(" -> Connection failed") 

    @cherrypy.expose
    def captures(self, **params):
        try:
            if 'pass' in params and params["pass"] == pass_capture:

                data="<h1>Captures</h1>"
                files = os.scandir(directory+"/server/captures/")
                for x in files:
                    _, ext = os.path.splitext(x.name)
                    if ext == '.jpg' or ext == '.png' or ext == '.gif':
                        data+="<img style='width:320; height:240;' src='/annexes/"+x.name+"'>"
                    if ext == '.mp4' or ext == '.mkv':
                        data+="<video controls style='width:320; height:240;' src='/annexes/"+x.name+"'></video>"
                cherrypy.log(" -> Captures viewed") 
                return data
        except:
            cherrypy.log(" -> Connection failed")

    @cherrypy.expose
    def log(self, **params):
        try:
            if params["pass"] and params["pass"] == pass_capture:
                logfile = open(directory+'/../log/aya.log', 'r')
                return """<html><head><meta http-equiv="refresh" content="5" /></head>
                <body>"""+logfile.read()+"""</body>
                <script>window.scrollTo(0,document.body.scrollHeight); </script></html>"""
                logfile.close()
        except:
            pass

def error_page(status, message, traceback, version):
    return "Error"

def validate_password(realm, username, password):
    if username in USERS and USERS[username] == password:
       return True
    return False

cherrypy.config.update({'error_page.401': error_page})
cherrypy.config.update({'error_page.402': error_page})
cherrypy.config.update({'error_page.403': error_page})
cherrypy.config.update({'error_page.404': error_page})
cherrypy.config.update({'error_page.500': error_page})
cherrypy.config.update({"tools.staticdir.root":os.getcwd()})
#cherrypy.config.update({'log.screen': False,                                                
                        #'log.access_file': directory+'/../log/cherrypy_access.log',
                        #'log.error_file': directory+'/../log/cherrypy_error.log'})      # set log True/False


conf = {                        # 8089 ou 443
   '/protected/area': {
       'tools.auth_basic.on': True,
       'tools.auth_basic.realm': 'localhost',
       'tools.auth_basic.checkpassword': validate_password
    },
    'global':{
        'server.socket_host': "0.0.0.0", 
        'server.socket_port': 8080,
        'server.thread_pool': 5,
        'tools.sessions.on': True, 
        'tools.encode.encoding': "Utf-8"
    },
    '/annexes':{
        'tools.staticdir.on': True,
        'tools.staticdir.dir': directory+"/server/captures" 
    },
    '/file':{
        'tools.staticdir.on': True,
        'tools.staticdir.dir': directory 
    }
}    

#if __name__ == "__main__":
#    cherrypy.quickstart(font_end(), '/', conf)
 #       'server.ssl_module':'builtin',
  #      'server.ssl_certificate':'cert.pem',
   #     'server.ssl_private_key':'privkey.pem',