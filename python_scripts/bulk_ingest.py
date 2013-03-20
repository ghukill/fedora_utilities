#bulk ingest script to Fedora Commons (testing)
#run from directory of FOXML files...

#example request:
#curl -i -u fedoraAdmin:fedoraAdmin -X POST http://[hostName]/fedora/objects/new -H "Content-Type: text/xml" --data-binary "@cfai_EB02b012.xml"

import os
from string import Template
import sys
import time

#variables
ingest_files = []
loghand = open('log.txt','w')


#get list of files in current directory, send to "ingest_files"
file_list = os.listdir('.')
for item in file_list:
	if item.endswith('.xml'):
		ingest_files.append(item.strip())


#ingest FOXML file with Fedora RESTful API
for ingest_file in ingest_files:
	
	try:
		os.system(Template('curl -i -u fedoraAdmin:cowp00p2012 -X POST http://141.217.172.152/fedora/objects/new -H "Content-Type: text/xml" --data-binary "@$ingest_file"').substitute(ingest_file=ingest_file))
		print "Object "+ingest_file+" successfully ingested."
		time.sleep(.5)
	except:
		print "******** Could not ingest object "+ingest_file+" ********"
		loghand.write("******** Could not ingest object "+ingest_file+" ********\n")
		continue
	
#closes logs
loghand.close()
