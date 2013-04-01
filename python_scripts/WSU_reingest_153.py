#indexes and ingests already processed files
#helpful for re-ingesting ebook objects during testing

#all objects assumed to be in /var/www/data

import os
from string import Template
import sys

print "This script will re-index and re-ingest objects into 153.  Assumes all items are in /var/www/data.  Ctrl(or Command)+C to exit now, or press a key to continue."
raw_input()


################################################################
# function to generate full paths
def listdir_fullpath(d):
    return [os.path.join(d, f) for f in os.listdir(d)]
################################################################

#ingest into Fedora
ingestList = listdir_fullpath('/var/www/data')
for itemPath in ingestList:
	try:
		#index Solr
		os.system(Template("bash /var/opt/solr_utilities/reindex_153.sh $itemPath").substitute(itemPath=itemPath))
		print "item indexed."

		#ingest objects
		os.system(Template("python /var/opt/fedora_utilities/python_scripts/WSU-PDF_bulk_ingest_153.py $itemPath").substitute(itemPath=itemPath))
	except:
		print "something broke..."


print "all done."





