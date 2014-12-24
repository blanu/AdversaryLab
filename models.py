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
  pcap=db.ReferenceProperty(PcapFile)
  duration=db.ListProperty(float)
  incomingStats=db.ReferenceProperty(DirectionalSummaryStats, collection_name="incomingStats")
  outgoingStats=db.ReferenceProperty(DirectionalSummaryStats, collection_name="outgoingStats")

class DirectionalSummaryStats(db.Model):
  lengths=db.ListProperty(int)
  content=db.ListProperty(int)
  entropy=db.ListProperty(float)
  flow=db.ListProperty(int)

class Stats(db.Model):
  lengths=db.ListProperty(int)
  content=db.ListProperty(int)
  entropy=db.FloatProperty(required=True)
  flow=db.ListProperty(int)

class PcapFile(db.Model):
  uploader=db.UserProperty(required=True)
  filename=db.StringProperty(required=True)
  filekey=blobstore.BlobReferenceProperty(required=True)
  status=db.IntegerProperty(required=True)
  port=db.IntegerProperty(required=True)
  protocol=db.ReferenceProperty(Protocol, required=False)
  dataset=db.ReferenceProperty(Dataset, required=False)

class Connection(db.Model):
  pcap=db.ReferenceProperty(PcapFile)
  portsId=db.StringProperty(required=False)
  duration=db.FloatProperty(required=False)
  incomingStats=db.ReferenceProperty(Stats, collection_name='incomingStats')
  outgoingStats=db.ReferenceProperty(Stats, required=False, collection_name='outgoingStats')

class AdversaryModel(db.Model):
  name=db.StringProperty(required=True)

class LabeledData(db.Model):
  adversary=db.ReferenceProperty(AdversaryModel, required=True)
  pcap=db.ReferenceProperty(PcapFile, required=True)
  label=db.BooleanProperty(required=True)
  training=db.BooleanProperty(required=True)
