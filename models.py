""" The models module provides App Engine db.Model classes for storing freefall models in the App Engine database. """

from google.appengine.ext import db
from google.appengine.ext import blobstore

class Protocol(db.Model):
  creator=db.UserProperty(required=True)
  name=db.StringProperty(required=True)

class Dataset(db.Model):
  creator=db.UserProperty(required=True)
  name=db.StringProperty(required=True)

class PcapFile(db.Model):
  uploader=db.UserProperty(required=True)
  filename=db.StringProperty(required=True)
  filekey=blobstore.BlobReferenceProperty(required=True)
  status=db.IntegerProperty(required=True)
  port=db.IntegerProperty(required=True)
  protocol=db.ReferenceProperty(Protocol, required=False)
  dataset=db.ReferenceProperty(Dataset, required=False)

class Connection(db.Model):
  pcap=db.ReferenceProperty(PcapFile, required=True)
  incomingPort=db.IntegerProperty(required=True)
  outgoingPort=db.IntegerProperty(required=True)

class Stream(db.Model):
  connection=db.ReferenceProperty(Connection, required=True)
  srcPort=db.IntegerProperty(required=True)
  dstPort=db.IntegerProperty(required=True)

class Packet(db.Model):
  stream=db.ReferenceProperty(Stream, required=True)
  length=db.IntegerProperty(required=True)
  entropy=db.FloatProperty(required=True)
  content=db.ListProperty(int)
  timestamp=db.IntegerProperty(required=True)
