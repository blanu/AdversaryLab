import logging

from google.appengine.api import urlfetch
from google.appengine.ext import db
from google.appengine.ext import blobstore

import status
from models import *

def processPcap(blobkey):
  blob_info=blobstore.get(blobkey)
  logging.info("processing "+blob_info.filename)

  pcap=PcapFile.all().filter("filekey =", blobkey).get()
  pcap.status=status.processing
  pcap.save()

  urlfetch.fetch("http://blanu.net:8085/%s" % (blobkey))
