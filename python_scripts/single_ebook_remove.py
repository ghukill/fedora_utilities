#utility to remove individual ebooks

import os
from string import Template
import sys
import pycurl, json
import urllib
import cStringIO
import json
import time

#expecting ebook PID as argument 1, Fedora relationship as argument 2
ebookPID = sys.argv[1]
relationship = sys.argv[2]
baseURL = '141.217.172.45'

#variables
response = cStringIO.StringIO()
pid_list = []
tuple_query_list = []

#Create Queries
base_tup_url = Template("http://$baseURL/fedora/risearch?").substitute(baseURL=baseURL)
user_pwd = "fedoraAdmin:fedoraAdmin"

tuple_query = Template('select ?object from <#ri> where ?object <info:fedora/fedora-system:def/relations-external#$relationship> <info:fedora/$ebookPID>').substitute(ebookPID=ebookPID,relationship=relationship)
tuple_query_list.append(tuple_query)

def getPIDsQuery(tuple_query_list):
	for tuple_query in tuple_query_list:
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

		try:
			#create list of objects, then push to array 
			objects = csv_response.split('\n')
			# print objects
			objects.pop(0)
			objects.pop(-1)

			for each in objects:
				pid_list.append(each.split("/")[1].strip())

			print pid_list
		except:
			continue

getPIDsQuery(tuple_query_list)

#Iterate through PID's, purge objectcs
for pid in pid_list:
	
	try:
		os.system(Template('curl -i -u fedoraAdmin:fedoraAdmin -X DELETE http://$baseURL/fedora/objects/$pid').substitute(baseURL=baseURL,pid=pid))
		print "Ojbect "+pid+" removed."
		time.sleep(2)
	except:
		print "Could not remove "+pid		
		continue

#finally, purge object itself
os.system(Template('curl -i -u fedoraAdmin:fedoraAdmin -X DELETE http://$baseURL/fedora/objects/$ebookPID').substitute(baseURL=baseURL,ebookPID=ebookPID))
print "Ojbect "+pid+" removed."

