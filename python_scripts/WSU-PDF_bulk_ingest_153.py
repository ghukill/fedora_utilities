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

#function for full file paths
def listdir_fullpath(d):
    return [os.path.join(d, f) for f in os.listdir(d)]

#catch item to be ingested
#CONSIDER CATCHING FOR TRAILING "/"
itemPath = sys.argv[1]

#get list of files in current directory, send to "ingest_files"
ingestPath = itemPath + "/" + itemPath.split('/')[-1] + "_INGEST"

file_list = listdir_fullpath(ingestPath)
print "Ingesting the following files:",file_list
for ingest_file in file_list:

	
#ingest FOXML file with Fedora RESTful API
	if ingest_file.endswith('.xml'):

		try:
			os.system(Template('curl -i -u fedoraAdmin:cowp00p2012 -X POST http://141.217.172.153:8080/fedora/objects/new -H "Content-Type: text/xml" --data-binary "@$ingest_file"').substitute(ingest_file=ingest_file))
			print "Ojbect "+ingest_file+" successfully ingested."
			time.sleep(1)

		except:
			#this does not work...need to read response headers to catch errors on this front...
			print "******** Could not ingest object "+ingest_file+" ********"
			loghand.write("******** Could not ingest object "+ingest_file+" ********\n")
			continue
	
#closes logs
loghand.close()
print "Item successful!"
