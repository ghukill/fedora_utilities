#ABOUT
# this file is designed to process incmoing files from Abbyy for use in the eText Reader
# incoming folder = "/abbyyoutput/bookreader"
# processing folder = "/processing"
# output = "var/www/data"

#IMPROVEMENTS
# 1) Consider changing all "os.command" to "subprocess.call ( e.g. from subprocess import call --> call(['ls','*.pdf']) )
	#os.command creates potential race conditions, might be a problem for larger files.	
# 2) Use either middle page of book, or average of page dimension ratios for book overall ratio (lines 215,216)

import os
from string import Template
import shutil
from elementtree.SimpleXMLWriter import XMLWriter
import sys
import Image
import re
from bs4 import BeautifulSoup


######################################################################################################################
# WORKING FROM /abbyyoutput/bookreader
######################################################################################################################

#MOVE ALL ITEMS TO PROCESSING FOLDER
#Not doing this for now - it might make sense to be able to run this script when nothing is changing on the Abbyy output folder, that was always kind of the idea...
# try:
# 	os.system("mv /abbyybookreader/* /processing")
# 	print "all items moved."
# except:
# 	"didn't move anything... maybe they are already there?"


def directoryRename():
	#get list of directories
	pre_item_ID_list = os.listdir('/processing')
	if len(pre_item_ID_list) == 0:
		print "Nothing to do!"		
	else:
		print "Processing these items: ",pre_item_ID_list

	#prepare normalized list
	item_ID_list = []
	for item_ID in pre_item_ID_list:		
		#apostrophes
		item_ID_handle = re.sub("'","\\'", item_ID)
		n_item_ID = re.sub(" ","_", item_ID)
		#spaces
		item_ID_handle = re.sub(" ","\ ", item_ID_handle)
		n_item_ID = re.sub("'","", n_item_ID)				
		# item_ID = unidecode(item_ID) #uncomment to use - works, but ugly
		print item_ID,"-->",item_ID_handle		
		os.system(Template("mv /processing/$item_ID_handle /processing/$n_item_ID").substitute(item_ID_handle=item_ID_handle,n_item_ID=n_item_ID))

	item_ID_list = os.listdir('/processing')
	return item_ID_list

# change permissions en bulk
def permissionsChange(item_ID_list):
	for item_ID in item_ID_list:
		os.system(Template("chmod -R 755 /processing/$item_ID").substitute(item_ID=item_ID))


#try to get MODS file


# remove PDF artifacts (PNGs), renames images to match item_ID
def fileRename(item_ID):

	#remove PNG files
	os.system(Template("rm /processing/$item_ID/*.png").substitute(item_ID=item_ID))

	images = os.listdir("/processing/"+item_ID)
	images.sort() #sorts images
	image_num = 1 #this method only works with htm, pdf, and image / if 
	count = 0
	for image in images:
		# get image type
		image_type = image.split(".")
		image_type = image_type[len(image_type)-1]
		
		# contruct image name
		new_image_name = item_ID + str(image_num).zfill(5) + "." + image_type
		# rename file
		os.system(Template("mv /processing/$item_ID/$image /processing/$item_ID/$new_image_name").substitute(item_ID=item_ID, image=image, new_image_name=new_image_name))

		#bumps counters		
		if count == 3:
			count = 0
			image_num = image_num + 1
		else:
			count = count + 1		


def imageResize (item_ID):
	images = os.listdir("/processing/"+item_ID)
	for image in images:
		# accepted_image_types = ['jpg','jpeg','tif','tiff','gif','png']
		accepted_image_types = ['jpg'] #expecting only jpg images from WSU PDF route, because essentially the PDF is the definitive copy, not archival TIFFs
		image_basename, image_type = image.split('.')[0], image.split('.')[-1]
		if image_type.lower() in accepted_image_types: #looking for jpg or tif

			# max dimensions, change this for finding "sweet spot" in bookreader
			max_width = 1700
			max_height = 1700			
			
			
			# get dimensions
			im = Image.open(Template('/processing/$item_ID/$image').substitute(item_ID=item_ID, image=image))						
			width, height = im.size #returns tuple			

			if height > width:				
				print Template("Portait - resizing from $orig_height to 1700").substitute(orig_height=height)				
				im.thumbnail((max_width, max_height), Image.ANTIALIAS)
				# converts to RGB if necessary...
				if im.mode != "RGB":
					im = im.convert("RGB")				
				im.save(Template('/processing/$item_ID/$image_basename.jpg').substitute(item_ID=item_ID, image_basename=image_basename))
				print image,"resized to: ",im.size,", converted to JPEG."				

			else:
				print Template("Portait - resizing from $orig_width to 1700").substitute(orig_width=width)				
				im.thumbnail((max_width, max_height), Image.ANTIALIAS)
				# converts to RGB if necessary...
				if im.mode != "RGB":
					im = im.convert("RGB")				
				im.save(Template('/processing/$item_ID/$image_basename.jpg').substitute(item_ID=item_ID, image_basename=image_basename))
				print image,"resized to: ",im.size,", converted to JPEG."				

		else:
			continue		

def createThumbs (item_ID):
	os.system(Template("mkdir /processing/$item_ID/thumbs").substitute(item_ID=item_ID))

	images = os.listdir("/processing/"+item_ID)
	for image in images:
		if image.endswith('jpg'): #derivative copy from tiffs
			image_basename = image.split('.')[0]
			thumb_width = 200
			thumb_height = 200

			# get dimensions
			im = Image.open(Template('/processing/$item_ID/$image').substitute(item_ID=item_ID, image=image))						
			width, height = im.size #returns tuple	

			if height > width:				
				print "Portait - creating thumbnail"
				im.thumbnail((thumb_width, thumb_height), Image.ANTIALIAS)
				thumbname = image_basename
				im.save(Template('/processing/$item_ID/thumbs/$thumbname.jpg').substitute(item_ID=item_ID, thumbname=thumbname))
				print image,"thumbnail created."				

			else:
				print Template("Portait - creating thumbnail").substitute(orig_width=width)				
				im.thumbnail((thumb_width, thumb_height), Image.ANTIALIAS)			
				thumbname = image_basename
				im.save(Template('/processing/$item_ID/thumbs/$thumbname.jpg').substitute(item_ID=item_ID, thumbname=thumbname))
				print image,"thumbnail created."
		else:
			continue


# function to move and create file structure
def createStructure(item_ID):
	
	#images
	os.system(Template("mkdir /processing/$item_ID/images").substitute(item_ID=item_ID))
	try:
		os.system(Template("mv /processing/$item_ID/*.jpg /processing/$item_ID/images").substitute(item_ID=item_ID))
	except:
		print "no images to move."

	########################################################################################################################
	#original tiffs
	os.system(Template("mkdir /processing/$item_ID/tiffs").substitute(item_ID=item_ID))
	try:
		os.system(Template("mv /processing/$item_ID/*.tif /processing/$item_ID/tiffs").substitute(item_ID=item_ID))
	except:
		print "no original images to move."
	########################################################################################################################

	#images/thumbs
	os.system(Template("mkdir /processing/$item_ID/images/thumbs").substitute(item_ID=item_ID))
	try:
		os.system(Template("mv /processing/$item_ID/thumbs/* /processing/$item_ID/images/thumbs/").substitute(item_ID=item_ID))
		os.system(Template("rm -R /processing/$item_ID/thumbs/").substitute(item_ID=item_ID))				
	except:
		print "no images to move."

	#OCR		
	os.system(Template("mkdir /processing/$item_ID/OCR").substitute(item_ID=item_ID))
	try:
		os.system(Template("mv /processing/$item_ID/*.htm /processing/$item_ID/OCR").substitute(item_ID=item_ID))
	except:
		print "no OCR / html to move."

	#altoXML		
	os.system(Template("mkdir /processing/$item_ID/altoXML").substitute(item_ID=item_ID))
	try:
		os.system(Template("mv /processing/$item_ID/*.xml /processing/$item_ID/altoXML").substitute(item_ID=item_ID))
	except:
		print "no altoXML to move."

	#pdf
	os.system(Template("mkdir /processing/$item_ID/pdf").substitute(item_ID=item_ID))
	try:
		os.system(Template("mv /processing/$item_ID/*.pdf /processing/$item_ID/pdf").substitute(item_ID=item_ID))
	except:
		print "no pdf's to move."

	#fullbook
	os.system(Template("mkdir /processing/$item_ID/fullbook").substitute(item_ID=item_ID))


	print Template("file structure created for $item_ID").substitute(item_ID=item_ID)


######################################################################################################################
# WORKING FROM /processing now
######################################################################################################################

# function to create metadata file for each item_ID from "/processing" dir
def createMetadata(item_ID):
	# get number of files
	images = os.listdir("/processing/"+item_ID+"/images")
	leaf_count = len(images) - 1 #accounts for /thumbs directory in there		

	# get dimensions of cover and create cover image
	cover_path = Template('/processing/$item_ID/images/$item_ID').substitute(item_ID=item_ID) + "00001.jpg"
	im = Image.open(cover_path)
	width, height = im.size #returns tuple

	# generate cover thumbnail
	max_cover_width = 200
	max_cover_height = 200
	im.thumbnail((max_cover_width, max_cover_height), Image.ANTIALIAS)				
	im.save(Template('/processing/$item_ID/$item_ID').substitute(item_ID=item_ID) + "_cover.jpg")
	print "Cover created for",item_ID	

	# write to xml
	fhand = Template("/processing/$item_ID/$item_ID$suffix.xml").substitute(item_ID=item_ID, suffix="_metadata")
	w = XMLWriter(fhand, "utf-8")

	metadata = w.start("add")
	w.start("doc")
	w.element("field", Template("meta:$item_ID").substitute(item_ID=item_ID), name="id") 
	w.element("field", Template("$item_ID").substitute(item_ID=item_ID), name="ItemID") #no underscore for solr index in "ItemID"
	#creats overall ratio - height / width
	w.element("field", str(height), name="pheight")
	w.element("field", str(width), name="pwidth")
	w.element("field", str(leaf_count), name="leafs")
	w.element("field", Template("$item_ID").substitute(item_ID=item_ID), name="item_title") #how will we generate this? ItemID for now... 
	w.end() #closes <doc>

	w.close(metadata)

def createSinglePDF(item_ID):
	os.system(Template("pdftk /processing/$item_ID/pdf/*.pdf cat output /processing/$item_ID/pdf/$item_ID.pdf").substitute(item_ID=item_ID))
	print "merged pdf created."
	#move concatenated file to "fullbook"
	try:
		os.system(Template("mv /processing/$item_ID/pdf/$item_ID.pdf /processing/$item_ID/fullbook").substitute(item_ID=item_ID))
	except:
		print "could not move concatenated PDF."
	

def createSingleHTML(item_ID):
	#create meta-HTML file
	html_concat = ''

	#get list of HTML docs
	html_docs = os.listdir("/processing/"+item_ID+"/OCR")
	html_docs = sorted(html_docs) #sorts by ascending filename

	#iterate through them
	html_count = 1
	for html_doc in html_docs:
		fhand = open(Template('/processing/$item_ID/OCR/$html_doc').substitute(item_ID=item_ID, html_doc=html_doc),'r')		
		html_parsed = BeautifulSoup(fhand)
		print "HTML document parsed..."

		#sets div with page_ID
		html_concat = html_concat + Template('<div id="page_ID_$html_count" class="html_page">').substitute(html_count=html_count)
		
		#Set in try / except block, as some HTML documents contain no elements within <body> tag
		try:
			for block in html_parsed.body:				
				html_concat = html_concat + unicode(block)				
		except:
			print "<body> tag is empty, skipping. Adding page_ID anyway."
			continue

		#closes page_ID / div
		html_concat = html_concat + "</div>"

		html_count = html_count + 1
		fhand.close()

	#create concatenated file
	fwrite = open(Template('/processing/$item_ID/OCR/$item_ID').substitute(item_ID=item_ID)+".htm",'w')
	#convert to UTF-8
	html_concat = html_concat.encode('UTF-8')
	#write headers
	fwrite.write('<div id="html_concat_wrapper">\n')
	fwrite.write('<meta http-equiv="content-type" content="text/html; charset=UTF-8">\n')	
	fwrite.write(html_concat)
	fwrite.write('\n</div>')
	fwrite.close()

	# move concatenated file to "fullbook"
	try:
		os.system(Template("mv /processing/$item_ID/OCR/$item_ID.htm /processing/$item_ID/fullbook").substitute(item_ID=item_ID))
		print "Concatenated, encoded HTML document created."
	except:
		print "could not move concatenated HTML."	
	

# index item_ID's in Solr
def indexItemsinSolr(item_ID):
	#run index item script
	os.system(Template("bash /var/opt/solr_utilities/sindex_item_152.sh $item_ID").substitute(item_ID=item_ID))
	print "item indexed."

# move files from /processing to /var/www/data
# this will fail if there is something there already
def movetoData():
	os.system("mv /processing/* /var/www/data")


def processItems(item_ID_list):
	for item_ID in item_ID_list:
		try:
			fileRename(item_ID)
			# raw_input("File RENAME complete, click enter to continue...")
			imageResize(item_ID)
			# raw_input("File RESIZE complete, click enter to continue...")
			createThumbs(item_ID)
			# raw_input("Thumbs CREATE complete, click enter to continue...")
			createStructure(item_ID)
			# raw_input("item_ID STRUCTURE complete, click enter to continue...")
			createMetadata(item_ID)
			# raw_input("item_ID METADATA complete, click enter to continue...")
			createSinglePDF(item_ID)
			# raw_input("item_ID SinglePDF complete, click enter to continue...")
			createSingleHTML(item_ID)
			# raw_input("item_ID SingleHTML complete, click enter to continue...")
			indexItemsinSolr(item_ID)
			# raw_input("item_ID INDEXING complete, click enter to continue...")
			print item_ID,"complete!"
		except:
			#this should include a logging event
			print item_ID, "did NOT complete, errors were had."
			os.system(Template("mv /processing/$item_ID/ /exceptions").substitute(item_ID=item_ID))

#Go!
item_ID_list = directoryRename() #REQUIRED
permissionsChange(item_ID_list)
processItems(item_ID_list)

print "All files processed, great success!"



# After MIM ingest, it would make sense to change the structure above.
# Currently it concatenates "/processing" with the ItemID, this works, but is not as forgiving as using this "listdir_fullpath" function
# As it stands, FOXML manifest creation and ingest will occur AFTER all the books have been ordered, structured, and indexed in Solr.
# Not the end of the world, but would be nice for entire books to fail.


#run pre-FOXML Manifest Creation utility
# function to generate full paths
def listdir_fullpath(d):
    return [os.path.join(d, f) for f in os.listdir(d)]

manifest_list = listdir_fullpath('/processing')
print "Creating pre-FOXML manifests for the following items:",manifest_list
for item_path in manifest_list:
	try:
		os.system(Template("python /var/opt/fedora_utilities/python_scripts/WSU-PDF_ebook_manifest_create_152.py $item_path WSUpress").substitute(item_path=item_path))
	except:
		#this should include a logging event
		print item_path,"had errors and did NOT process."
		os.system(Template("mv /processing/$item_ID/ /exceptions").substitute(item_ID=item_ID))


#run Saxon transformation, creating FOXML files for ebook object and consituent parts
print "Creating FOXML 1.1 files for the following items:",manifest_list
for item_path in manifest_list:
	try:
		os.chdir(item_path)
		os.system('java -jar /var/opt/fedora_utilities/saxon9he.jar *_manifest.xml http://141.217.97.167/xslt_sheets/ebook_FOXEYMOLE_creator_LIVE.xsl')
		print item_path,"success!"
	except:
		#this should include a logging event
		print item_path,"had errors and did NOT process."
		os.system(Template("mv /processing/$item_ID/ /exceptions").substitute(item_ID=item_ID))

#move to pedestal / data folder for ingest into Fedora
#this will fail if there is something there already...
movetoData()

#ingest into Fedora
ingestList = listdir_fullpath('/var/www/data')
for itemPath in ingestList:
	try:
		os.system(Template("python /var/opt/fedora_utilities/python_scripts/WSU-PDF_bulk_ingest_152.py $itemPath").substitute(itemPath=itemPath))
	except:
		#this should include a logging event
		print item_path,"had errors and did NOT process."
		os.system(Template("mv itemPath /exceptions").substitute(itemPath=itemPath))


#A final step would be cleaning up data directory; or perhaps moving these files to a "to_be_removed" directory

## ---------------------- ##
# Define an error / exception function
# alert errors, moves to exceptions folder, and logs what the error was to a central log somewhere






