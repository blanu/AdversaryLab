""" The models module provides App Engine db.Model classes for storing freefall models in the App Engine database. """

from google.appengine.ext import db
from google.appengine.ext import blobstore

class Protocol(db.Model):
  creator=db.UserProperty(required=True)
  name=db.StringProperty(required=True)

class Dataset(db.Model):
  creator=db.UserProperty(required=True)
  name=db.StringProperty(required=True)

class Stats(db.Model):
  lengths=db.ListProperty(int)
  content=db.ListProperty(int)
  durations=db.ListProperty(float)
  entropies=db.ListProperty(float)
  flow=db.ListProperty(int)

class PcapFile(db.Model):
  uploader=db.UserProperty(required=True)
  filename=db.StringProperty(required=True)
  filekey=blobstore.BlobReferenceProperty(required=True)
  status=db.IntegerProperty(required=True)
  port=db.IntegerProperty(required=True)
  protocol=db.ReferenceProperty(Protocol, required=False)
  dataset=db.ReferenceProperty(Dataset, required=False)
  incomingStats=db.ReferenceProperty(Stats, required=False, collection_name='incomingStats')
  outgoingStats=db.ReferenceProperty(Stats, required=False, collection_name='outgoingStats')
