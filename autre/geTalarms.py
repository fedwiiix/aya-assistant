
from requests.auth import HTTPDigestAuth
import requests, json

headers = {'User-Agent': 'Mozilla/5.0 Chrome/39.0.2171.95 Safari/537.36'}
r = requests.get("https://sjtm.fr/domotix/database/get_db.php?request=alarmes", auth=HTTPDigestAuth('aiaUser', 'aecoenplaienghdjk198sd56'), headers=headers)

decoded = json.loads((r.content).decode("utf-8"))

alarmes='{ "number":"'+str(len(decoded['alarmes']))+'","alarmes":['
for x in decoded['alarmes']:
    alarmes+= '''{"action": "'''+x['action_alarme']+'''","repeter": "'''+x['repeter_alarme']+'''","heure": "'''+x['heure_alarme']+'''","status": "'''+x['status_alarme']+'''","appareil": "'''+x['appareil_alarme']+'''","cmd": "'''+x['cmd']+'''"},'''

alarmes=alarmes[:-1]+"]}"
print(alarmes)