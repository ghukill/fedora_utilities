# this file is designed to process incmoing files from the Abbyy VM for use in the eText Reader
# incoming folder = "/incoming"
# processing folder = "/processing"
# output = "var/www/data"

import os
from string import Template
import shutil
from elementtree.SimpleXMLWriter import XMLWriter
import sys
import Image
import re

#get list of directories (item_ID's)
item_ID_list = os.listdir('/var/www/data/')
print "Creating covers for the following: ",item_ID_list


# function to create metadata file for each item_ID from "/processing" dir
def createCoverThumbnail(item_ID):
	# get number of files
	images = os.listdir("/var/www/data/"+item_ID+"/images")	

	# get dimensions of cover and create cover image
	cover_path = Template('/var/www/data/$item_ID/images/$item_ID').substitute(item_ID=item_ID) + "00001.jpg"
	im = Image.open(cover_path)
	width, height = im.size #returns tuple

	# generate cover thumbnail
	max_cover_width = 200
	max_cover_height = 200
	im.thumbnail((max_cover_width, max_cover_height), Image.ANTIALIAS)				
	im.save(Template('/var/www/data/$item_ID/$item_ID').substitute(item_ID=item_ID) + "_cover.jpg")
	print "Cover created for",item_ID


def processItems(item_ID_list):
	for item_ID in item_ID_list:
		
		createCoverThumbnail(item_ID)
		# raw_input("item_ID COVER CREATION complete, click enter to continue...")
		print item_ID,"complete!"

#Go!
processItems(item_ID_list)


	




