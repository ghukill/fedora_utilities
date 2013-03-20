#bulk remove files

#example request:
# curl -i -u fedoraAdmin:fedoraAdmin -X DELETE http://141.217.172.45:8080/fedora/objects/{PID}

#iterate through PIDs, purge from Fedora

import os
from string import Template
import sys
import pycurl, json
import urllib
import cStringIO
import json
import time

#variables
response = cStringIO.StringIO()
pid_list = []

#Get PID's for a collection
base_tup_url = "http://localhost:8080/fedora/risearch?"
user_pwd = "fedoraAdmin:fedoraAdmin"
tuple_query = 'select $object from <#ri> where $object <info:fedora/fedora-system:def/relations-external#isMemberOfCollection> <info:fedora/collection:ramsey>'

data = {
	"lang": "itql",
	"format": "CSV",
	"query": tuple_query 	
	}

c = pycurl.Curl()
c.setopt(pycurl.URL, base_tup_url + urllib.urlencode(data))
c.setopt(pycurl.USERPWD, user_pwd)
c.setopt(c.WRITEFUNCTION, response.write)
c.perform()

csv_response = response.getvalue()

#create list of objects, then push to array 
objects = csv_response.split('\n')
print objects
objects.pop(0)
objects.pop(-1)

for each in objects:
	pid_list.append(each.split("/")[1].strip())
print pid_list

#Iterate through PID's, add datastream for each
# for pid in pid_list:
# 	filename = pid.split(":")[1]
# 	# print Template('curl -i -u fedoraAdmin:fedoraAdmin -X POST "http://localhost:8080/fedora/objects/$pid/datastreams/THUMBNAIL?controlGroup=M&dsLabel=Thumbnail+for+$pid&mimeType=image%2Fjpeg&dsLocation=http%3A%2F%2F141.217.54.38%2F%7Eej2929%2Fdropbox%2Fcfai%2Fthumbs%2F$filename.jpg"').substitute(pid=pid,filename=filename)
# 	try:
# 		os.system(Template('curl -i -u fedoraAdmin:fedoraAdmin -X DELETE http://localhost:8080/fedora/objects/$pid').substitute(pid=pid))
# 		print "Ojbect "+pid+" removed."
# 		time.sleep(2)
# 	except:
# 		print "Could not remove "+pid
# 		raw_input()
# 		continue

