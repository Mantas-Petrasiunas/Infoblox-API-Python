import requests
import urllib3
import json
import csv
from pathlib import Path
from ipaddress import *


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
urlNet = "https://HOSTNAME/wapi/VERSION/network?_return_as_object=0&_return_fields=network,comment,authority,netmask,options,bootfile,bootserver,nextserver"
urlRng = "https://HOSTNAME/wapi/VERSION/range?_return_as_object=0&_return_fields=network,name,start_addr,end_addr,comment,network_view,disable,enable_ddns,exclude,options,nextserver,static_hosts,subscribe_settings"



payload={}
headers = {
  'Authorization': 'Basic XXX',
  'Cookie': 'ibapauth="group=admin-group,ctime=1648132671,ip=10.23.241.56,su=1,sessionID=1622484409,client=API,auth=LOCAL,timeout=6000,mtime=1648140096,user=admin,XXXXX"'
}

NetworksJSON = requests.request("GET", urlNet, headers=headers, data=payload, verify=False)
RangesJSON = requests.request("GET", urlRng, headers=headers, data=payload, verify=False)

#print(NetworksJSON.text)               #control output
#print(RangesJSON.text)                 #control output

NetworksTPL = NetworksJSON.json()
#print(NetworksTPL[0])                  #control output
RangesTPL = RangesJSON.json()
#print(RangesTPL[0])                    #control output

ParamList = []                          #defining an empty list for DHCP parameters



for rng_dict in RangesTPL:
    for net_dict in NetworksTPL:
        if rng_dict["network"] == net_dict["network"]:
            name = net_dict["comment"] if "comment" in net_dict else net_dict["network"]        #optain name from net_dict["comment"] if it exists
            option66 = net_dict["bootserver"] if "bootserver" in net_dict else ""
            option67 = net_dict["bootfile"] if "bootfile" in net_dict else ""
            optionUNKNOWN = net_dict["nextserver"] if "nextserver" in net_dict else ""          #next server option - unknown
            
            ip_network = IPv4Network(rng_dict["network"])                   #covert to IP address
            subnet_mask = ip_network.netmask                                #grab subnet mask
            net_id = ip_network.network_address                             #grap network address
            
            #Filter through the darn DHCP options in net_dict["options"] list of dictionaries
            #no idea how to re-use the code...
            #(https://www.delftstack.com/howto/python/python-search-list-of-dictionaries/#use-the-next-function-to-search-a-list-of-dictionaries-in-python)
            a = next((x for x in net_dict["options"] if x["num"] == 15), None)
            domain_name = a["value"] if a and a["num"] == 15 else ""           

            b = (next((x for x in net_dict["options"] if x["num"] == 3), None))
            router = b["value"] if b and b["num"] == 3 else ""            

            c = (next((x for x in net_dict["options"] if x["num"] == 6), None))
            domain_name_servers = c["value"] if c and c["num"] == 6 else ""

            d = (next((x for x in net_dict["options"] if x["num"] == 150), None))
            option150 = d["value"] if d and d["num"] == 150 else ""

            e = (next((x for x in net_dict["options"] if x["num"] == 160), None))
            option160 = e["value"] if e and e["num"] == 160 else ""

            f = (next((x for x in net_dict["options"] if x["num"] == 161), None))
            option161 = f["value"] if f and f["num"] == 161 else ""

            g = (next((x for x in net_dict["options"] if x["num"] == 191), None))
            option191 = g["value"] if g and g["num"] == 191 else ""

            h = (next((x for x in net_dict["options"] if x["num"] == 241), None))
            option241 = h["value"] if h and h["num"] == 241 else ""

            i = (next((x for x in net_dict["options"] if x["num"] == 46), None))
            option46 = i["value"] if i and i["num"] == 46 else ""
            #print ("***DHCP Parameters and options control output***")
            #print (rng_dict["network"],name,rng_dict["start_addr"],rng_dict["end_addr"],rng_dict["_ref"],domain_name,router,domain_name_servers,option150,option160,option161,option191,option241)

            #form a list [] of DHCP parameters and options and insert in to ParamList
            ParamList.append([net_id,name,rng_dict["start_addr"],rng_dict["end_addr"],subnet_mask,rng_dict["_ref"],domain_name,router,domain_name_servers,option46,option66,option67,option150,option160,option161,option191,option241,optionUNKNOWN])

#insert headers
ParamList.insert(0,["scopeid","name","startrange","endrange","subnetmask","comment","domain_name","router","domain_name_servers","option46","option66","option67","option150","option160","option161","option191","option241","optionUNKNOWN"])

#write to file without adding empty lines
home = str(Path.home())
file = open(f'{home}/dhcp_scopes.csv', 'w+', newline ='') 
with file:     
    write = csv.writer(file, delimiter =";") 
    write.writerows(ParamList)

print ("---DONE!---")
print ("The file 'dhcp_scopes.csv' was put to", home, "directory")   

