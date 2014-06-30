""" The models module provides App Engine db.Model classes for storing freefall models in the App Engine database. """

from google.appengine.ext import db
from google.appengine.ext import blobstore

class PcapFile(db.Model):
  uploader=db.UserProperty(required=True)
  filename=db.StringProperty(required=True)
  filekey=blobstore.BlobReferenceProperty(required=True)
  status=db.IntegerProperty(required=True)
  report=db.TextProperty(required=False)
    
