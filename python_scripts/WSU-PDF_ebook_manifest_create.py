#Fedora Commons WSUebook manifest creation utility

import os
from string import Template
import shutil
from elementtree.SimpleXMLWriter import XMLWriter
from elementtree.ElementTree import default_parser_api as XMLparser
import sys
import re
from datetime import datetime

'''
Script to create manifest of ebooks.  The resulting XML document will be an intermediate manifest of the file structure, that the XSLT stylesheet will then breakdown, and create individual FOXEYMOLE files for ingest into Fedora.  Bam!
'''

#Create timestamp
now_var = datetime.now() #time snapshot
t_stamp_concat_list = []
t_stamp_concat_list.extend( [str(now_var.year),str(now_var.month).zfill(2),str(now_var.day).zfill(2),str(now_var.hour).zfill(2),str(now_var.minute).zfill(2),str(now_var.second).zfill(2)] )
t_stamp = ''.join(t_stamp_concat_list[0:])
print "Timestamp for this ebook object:", t_stamp

#create some variables for writing XML
item_path = sys.argv[1]
if item_path.endswith("/"):
	item_ID = item_path.split('/')[-2]
else:
	item_ID = item_path.split('/')[-1]

print "***********************************************"
print "Item_ID: "+item_ID

# MemberOfCollections list
collections = ['WSUebooks'] #default "WSUebooks" collection
try:
	collections.append(sys.argv[2])		
except:
	pass

#PID-safe item_ID
PIDsafe = item_ID.replace('_','')

#get dimensions
filename=item_path+"/"+item_ID+"_metadata.xml"
fhand=open(filename,'r')
item_metadata_string = fhand.read()
meta_elements = XMLparser.fromstring(item_metadata_string)
pheight = meta_elements[0][2].text
pwidth = meta_elements[0][3].text
leafs = meta_elements[0][4].text
print "Height, Width, Leafs: "+pheight,pwidth,leafs

#get file counts:
page_images = sorted(os.listdir(item_path+'/images'))  #only folder with additional files inside, the thumbs
tiff_images = sorted(os.listdir(item_path+'/tiffs'))  
thumb_images = sorted(os.listdir(item_path+'/images/thumbs'))
HTML_docs = sorted(os.listdir(item_path+'/OCR'))
altoXML_docs = sorted(os.listdir(item_path+'/altoXML'))
pdf_docs = sorted(os.listdir(item_path+'/pdf'))
fullbook = sorted(os.listdir(item_path+'/fullbook'))

#base_URL
base_URL = "http://141.217.97.167/data"

#equality check
if (len(page_images) - 1) == len(thumb_images) == len(HTML_docs) == len(altoXML_docs) == len(pdf_docs):
	print "we have equality."

else:
	print "we do NOT have equality."
	choice = raw_input("Are you sure you want to continue (Y/n)?")

#Write datastreams manifest to XML
	#example datastream chunk
	'''
	<foxml:datastream CONTROL_GROUP="M" ID="ORIGINAL" STATE="A">
	    <foxml:datastreamVersion ID="ORIGINAL.0" MIMETYPE="image/jpeg" LABEL="Page#">
	        <foxml:contentLocation TYPE="URL">
	            <xsl:attribute name="REF">http://image.url/Sketches_and_scraps0000#.jpg</xsl:attribute>
	        </foxml:contentLocation>           
	    </foxml:datastreamVersion>
	</foxml:datastream>
	'''

fhand = item_path + "/" + item_ID + "_FOXML_manifest.xml"

w = XMLWriter(fhand, encoding="utf-8")
w.declaration()

#namespace dictionary
namespace={}
namespace['xmlns:foxml'] = "info:fedora/fedora-system:def/foxml#"
namespace['xmlns:xsi']="http://www.w3.org/2001/XMLSchema-instance"

manifest = w.start("ebook_item", namespace)

# iterate through parent collections and create <collection> elements for each
for collection_name in collections:
	w.element("collection", Template("$collection_name").substitute(collection_name=collection_name))

w.element("t_stamp", Template("$t_stamp").substitute(t_stamp=t_stamp))
w.element("book_title", Template("$item_ID").substitute(item_ID=item_ID))
w.element("item_ID", Template("$item_ID").substitute(item_ID=item_ID))
w.element("PIDsafe", Template("$PIDsafe").substitute(PIDsafe=PIDsafe))
w.start("dimensions")
w.element("pheight", Template("$pheight").substitute(pheight=pheight))
w.element("pwidth", Template("$pwidth").substitute(pwidth=pwidth))
w.element("leafs", Template("$leafs").substitute(leafs=leafs))
w.end('dimensions')
w.element("base_URL", Template("$base_URL/$item_ID").substitute(base_URL=base_URL,item_ID=item_ID))
w.start('objects')
## iterate to create image object datastreams #######################
w.start('images')
count = 1 #starts numbering of datastreams at "1" to better reflect relationship to physical pages
for each in page_images:
	if each != "thumbs":
		w.start('foxml:datastream',CONTROL_GROUP="M", ID=Template("IMAGE_$count").substitute(count=str(count)), STATE="A")
		w.start('foxml:datastreamVersion',MIMETYPE="image/jpeg", ID=Template("IMAGE_$count.0").substitute(count=str(count)), LABEL=Template("Page Image $count").substitute(count=str(count)))
		w.start('foxml:contentLocation',TYPE="URL",REF=Template("$base_URL/$item_ID/images/$each").substitute(base_URL=base_URL,item_ID=item_ID,each=each))	
		w.end('foxml:contentLocation')
		w.end('foxml:datastreamVersion')
		w.end('foxml:datastream')
		count += 1
w.end('images')		

## iterate to create thumb object datastreams #######################
w.start('thumbs')
count = 1 #starts numbering of datastreams at "1" to better reflect relationship to physical pages
for each in thumb_images:
	w.start('foxml:datastream',CONTROL_GROUP="M", ID=Template("THUMB_$count").substitute(count=str(count)), STATE="A")
	w.start('foxml:datastreamVersion',MIMETYPE="image/jpeg", ID=Template("THUMB_$count.0").substitute(count=str(count)), LABEL=Template("Page Thumb $count").substitute(count=str(count)))
	w.start('foxml:contentLocation',TYPE="URL",REF=Template("$base_URL/$item_ID/images/thumbs/$each").substitute(base_URL=base_URL,item_ID=item_ID,each=each))	
	w.end('foxml:contentLocation')
	w.end('foxml:datastreamVersion')
	w.end('foxml:datastream')
	count += 1
w.end('thumbs')	

## iterate to create thumb object datastreams #######################
## If these are NOT Tiffs, the mime/type will have to be determined elsewhere...
w.start('tiffs')
count = 1 #starts numbering of datastreams at "1" to better reflect relationship to physical pages
for each in tiff_images:
	w.start('foxml:datastream',CONTROL_GROUP="M", ID=Template("ORIGINAL_$count").substitute(count=str(count)), STATE="A")
	w.start('foxml:datastreamVersion',MIMETYPE="image/tiff", ID=Template("ORIGINAL_$count.0").substitute(count=str(count)), LABEL=Template("Page Original $count").substitute(count=str(count)))
	w.start('foxml:contentLocation',TYPE="URL",REF=Template("$base_URL/$item_ID/tiffs/$each").substitute(base_URL=base_URL,item_ID=item_ID,each=each))	
	w.end('foxml:contentLocation')
	w.end('foxml:datastreamVersion')
	w.end('foxml:datastream')
	count += 1
w.end('tiffs')

## iterate to create HTML object datastreams #######################
w.start('HTML_docs')
count = 1 #starts numbering of datastreams at "1" to better reflect relationship to physical pages
for each in HTML_docs:
	w.start('foxml:datastream',CONTROL_GROUP="M", ID=Template("HTML_$count").substitute(count=str(count)), STATE="A")
	w.start('foxml:datastreamVersion',MIMETYPE="text/html", ID=Template("HTML_$count.0").substitute(count=str(count)), LABEL=Template("Page HTML $count").substitute(count=str(count)))
	w.start('foxml:contentLocation',TYPE="URL",REF=Template("$base_URL/$item_ID/OCR/$each").substitute(base_URL=base_URL,item_ID=item_ID,each=each))	
	w.end('foxml:contentLocation')
	w.end('foxml:datastreamVersion')
	w.end('foxml:datastream')
	count += 1
w.end('HTML_docs')	

## iterate to create altoXML object datastreams #######################
w.start('altoXML_docs')
count = 1 #starts numbering of datastreams at "1" to better reflect relationship to physical pages
for each in altoXML_docs:
	w.start('foxml:datastream',CONTROL_GROUP="M", ID=Template("altoXML_$count").substitute(count=str(count)), STATE="A")
	w.start('foxml:datastreamVersion',MIMETYPE="application/xml", ID=Template("altoXML_$count.0").substitute(count=str(count)), LABEL=Template("Page altoXML $count").substitute(count=str(count)))
	w.start('foxml:contentLocation',TYPE="URL",REF=Template("$base_URL/$item_ID/altoXML/$each").substitute(base_URL=base_URL,item_ID=item_ID,each=each))	
	w.end('foxml:contentLocation')
	w.end('foxml:datastreamVersion')
	w.end('foxml:datastream')
	count += 1
w.end('altoXML_docs')	

# iterate to create fullbook object datastreams #######################
w.start('fullbook_docs')
for each in fullbook:

	#HTML
	if each.endswith('.htm'):
		w.start('foxml:datastream',CONTROL_GROUP="M", ID="HTML_FULL", STATE="A")
		w.start('foxml:datastreamVersion',MIMETYPE="text/html", ID="HTML_FULL.0", LABEL=Template("Fulltext HTML for item").substitute(count=str(count)))
		w.start('foxml:contentLocation',TYPE="URL",REF=Template("$base_URL/$item_ID/fullbook/$each").substitute(base_URL=base_URL,item_ID=item_ID,each=each))	
		w.end('foxml:contentLocation')
		w.end('foxml:datastreamVersion')
		w.end('foxml:datastream')

	#PDF
	if each.endswith('.pdf'):
		w.start('foxml:datastream',CONTROL_GROUP="M", ID="PDF_FULL", STATE="A")
		w.start('foxml:datastreamVersion',MIMETYPE="text/pdf", ID="PDF_FULL.0", LABEL=Template("Fulltext PDF document for item").substitute(count=str(count)))
		w.start('foxml:contentLocation',TYPE="URL",REF=Template("$base_URL/$item_ID/fullbook/$each").substitute(base_URL=base_URL,item_ID=item_ID,each=each))	
		w.end('foxml:contentLocation')
		w.end('foxml:datastreamVersion')
		w.end('foxml:datastream')
	
w.end('fullbook_docs')	
##############################################################
w.end('objects')
w.close(manifest)

print "finis!"
print "***********************************************"




