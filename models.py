""" The models module provides App Engine db.Model classes for storing freefall models in the App Engine database. """

from google.appengine.ext import db
from google.appengine.ext import blobstore

class Protocol(db.Model):
  creator=db.UserProperty(required=True)
  name=db.StringProperty(required=True)

class Dataset(db.Model):
  creator=db.UserProperty(required=True)
  name=db.StringProperty(required=True)

class PcapStats(db.Model):
  lengths=db.ListProperty(int)
  entropies=db.ListProperty(float)

class PcapReport(db.Model):
  incoming=db.ReferenceProperty(PcapStats, collection_name="incoming_set", required=False)
  outgoing=db.ReferenceProperty(PcapStats, collection_name="outgoing_set", required=False)

class PcapFile(db.Model):
  uploader=db.UserProperty(required=True)
  filename=db.StringProperty(required=True)
  filekey=blobstore.BlobReferenceProperty(required=True)
  status=db.IntegerProperty(required=True)
  port=db.IntegerProperty(required=True)
  report=db.ReferenceProperty(PcapReport, required=False)
  protocol=db.ReferenceProperty(Protocol, required=False)
  dataset=db.ReferenceProperty(Dataset, required=False)
