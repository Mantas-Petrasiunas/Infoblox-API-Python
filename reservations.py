import requests
import urllib3
import json
import csv
from pathlib import Path
from ipaddress import *
import random
import string

def rand_mac():
    return "%02x-%02x-%02x-%02x-%02x-%02x" % (
        random.randint(0, 255),
        random.randint(0, 255),
        random.randint(0, 255),
        random.randint(0, 255),
        random.randint(0, 255),
        random.randint(0, 255)
        )


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
urlReservations = "https://HOSTNAME/wapi/VERSION/fixedaddress?_return_as_object=0&_return_fields=mac,ipv4addr,comment,disable,match_client,name,network,"


payload={}
headers = {
  'Authorization': 'Basic XXX',
  'Cookie': 'ibapauth="group=admin-group,ctime=1648132671,ip=10.23.241.56,su=1,sessionID=1622484409,client=API,auth=LOCAL,timeout=6000,mtime=1648140096,user=admin,XXX"'
}

ReservationsJSON = requests.request("GET", urlReservations, headers=headers, data=payload, verify=False)

#print(ReservationsJSON.text)               #control output

ReservationsTPL = ReservationsJSON.json()
#print (ReservationsTPL[0])

ParamList = []                              #reservation parameters list

for reservation in ReservationsTPL:
    ip = reservation["ipv4addr"]
    name = reservation["name"] if "name" in reservation else reservation["ipv4addr"]
    comment = str(reservation["comment"]) if "comment" in reservation else str(reservation["network"])
    scope_id = (IPv4Network(reservation["network"])).network_address        #convert reservation["network"] to IP addr and grab netwrok address only
    mac = (reservation["mac"]).replace(":","-")                                 #get mac and replace : with - to meet MS format
    if (mac and mac == "00-00-00-00-00-00"):
        mac = rand_mac()
        comment = comment+"  ---RANDOM MAC---"
        
    
    ParamList.append([name,ip,scope_id,mac,comment])

#insert headers
ParamList.insert(0, ["name","ip","scope_id","mac","comment"])
#print (ParamList)
    
#write to file without adding empty lines
home = str(Path.home())
file = open(f'{home}/dhcp_reservations.csv', 'w+', newline ='') 
with file:     
    write = csv.writer(file, delimiter =";") 
    write.writerows(ParamList)
    
print ("---DONE!---")
print ("The file 'dhcp_reservations.csv' was put to", home, "directory")



