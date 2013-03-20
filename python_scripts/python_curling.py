#addDadtastream, not really working...

import pycurl, json
import urllib

github_url = "http://localhost:8080/fedora/objects/cfai:EB01a002/datastreams/ORIGINAL"
user_pwd = "fedoraAdmin:fedoraAdmin"
data = json.dumps({
	"controlGroup": "M", 
	"dsLabel": "Original Image",
	"mimeType": urllib.quote_plus("image/jpeg"),
	"dsLocation": urllib.quote_plus("http://141.217.54.38/~ej2929/dropbox/cfai/EB01a002.tif")
	})

c = pycurl.Curl()
c.setopt(pycurl.URL, github_url)
c.setopt(pycurl.USERPWD, user_pwd)
c.setopt(pycurl.POST, 1)
c.setopt(pycurl.POSTFIELDS, data)
c.perform()