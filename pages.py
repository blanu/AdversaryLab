import re
import logging
import random
import base64
import struct
import time
import json

import urllib
from urllib import urlencode, unquote_plus

from google.appengine.ext import webapp
from google.appengine.ext import db
from google.appengine.ext import blobstore
from google.appengine.ext import deferred
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.api import users
from google.appengine.api import urlfetch
from google.appengine.api import mail

from json import loads, dumps

from airspeed import CachingFileLoader

import status
from generic import TemplatePage, GenericPage, FilePage
from models import *
from util import *
from process import *
from api import ReportService

class Index(TemplatePage):
  def processContext(self, method, user, req, resp, args, context):
    logging.debug("index")
    logging.debug(user)
    if not user:
      self.redirect('/welcome')
    else:
      self.redirect('/dashboard')

  def requireLogin(self):
    return False

class Welcome(TemplatePage):
  def processContext(self, method, user, req, resp, args, context):
    pass

  def requireLogin(self):
    return False

class Login(TemplatePage):
  def processContext(self, method, user, req, resp, args, context):
    self.redirect('/')

  def requireLogin(self):
    return True

class DashboardIndex(TemplatePage):
  def processContext(self, method, user, req, resp, args, context):
    logging.debug("dashboard index")
    context['userid']=user.email().lower()
    context['uploadUrl']=blobstore.create_upload_url('/upload')

    pcaps=PcapFile.all().filter("uploader =", user).order('status').run()
    context['pcaps']=pcaps
    logging.info('pcaps: '+str(pcaps))

    prots=Protocol.all().filter("creator =", user).order('name').run()
    context['prots']=prots
    logging.info('prots: '+str(prots))

    datasets=Dataset.all().filter("creator =", user).order('name').run()
    context['datasets']=datasets
    logging.info('datasets: '+str(datasets))

  def requireLogin(self):
    return True

class ManageDatasets(TemplatePage):
  def processContext(self, method, user, req, resp, args, context):
    logging.debug("dashboard index")
    context['userid']=user.email().lower()
    context['uploadUrl']=blobstore.create_upload_url('/upload')

    pcaps=PcapFile.all().filter("uploader =", user).order('status').run()
    context['pcaps']=pcaps
    logging.info('pcaps: '+str(pcaps))

    prots=Protocol.all().filter("creator =", user).order('name').run()
    context['prots']=prots
    logging.info('prots: '+str(prots))

    datasets=Dataset.all().filter("creator =", user).order('name').run()
    context['datasets']=datasets
    logging.info('datasets: '+str(datasets))

  def requireLogin(self):
    return True

class ManageProtocols(TemplatePage):
  def processContext(self, method, user, req, resp, args, context):
    logging.debug("dashboard index")
    context['userid']=user.email().lower()
    context['uploadUrl']=blobstore.create_upload_url('/upload')

    pcaps=PcapFile.all().filter("uploader =", user).order('status').run()
    context['pcaps']=pcaps
    logging.info('pcaps: '+str(pcaps))

    prots=Protocol.all().filter("creator =", user).order('name').run()
    context['prots']=prots
    logging.info('prots: '+str(prots))

    datasets=Dataset.all().filter("creator =", user).order('name').run()
    context['datasets']=datasets
    logging.info('datasets: '+str(datasets))

  def requireLogin(self):
    return True

class Organize(TemplatePage):
  def processContext(self, method, user, req, resp, args, context):
    logging.debug("dashboard index")
    context['userid']=user.email().lower()
    context['uploadUrl']=blobstore.create_upload_url('/upload')

    pcaps=PcapFile.all().filter("uploader =", user).order('status').run()
    context['pcaps']=pcaps
    logging.info('pcaps: '+str(pcaps))

    prots=Protocol.all().filter("creator =", user).order('name').run()
    context['prots']=prots
    logging.info('prots: '+str(prots))

    datasets=Dataset.all().filter("creator =", user).order('name').run()
    context['datasets']=datasets
    logging.info('datasets: '+str(datasets))

  def requireLogin(self):
    return True

# FIXME - Does not require authentication
class Upload(blobstore_handlers.BlobstoreUploadHandler):
  def post(self):
    user = users.get_current_user()

    port=self.validatePort(self.request.get('port'))
    if not port:
      logging.error("Invalid port: "+self.request.get('port'))
      self.redirect('/')
      return

    datasetname=self.request.get('pcapUploadDataset')
    protocolname=self.request.get('pcapUploadProtocol')

    upload_files = self.get_uploads('pcapFile')  # 'file' is file upload field in the form
    logging.info('upload_files: '+str(upload_files))
    blob_info = upload_files[0]
    blobkey = blob_info.key()
    filename=blob_info.filename

    parts=filename.split('.')[0].split('-')
    if len(parts)==4 and parts[0]=='sorted':
      protocolname=parts[2]
      datasetname=parts[3]

    dataset=Dataset.all().filter('dataset =', datasetname).get()
    protocol=Dataset.all().filter('protocol =', protocolname).get()

    pcap=PcapFile(filename=filename, uploader=user, filekey=blobkey, status=status.uploaded, port=port, dataset=dataset, protocol=protocol)
    pcap.save()

    deferred.defer(processPcap, blobkey)

    self.redirect('/')

  def validatePort(self, portString):
    if not portString:
      return None

    try:
      port=int(portString)
    except:
      return None

    if port<1 or port>65535:
      return None

    return port

# FIXME - Does not require authentication
class Download(blobstore_handlers.BlobstoreDownloadHandler):
  def get(self):
    filekey=self.request.get('filekey')

    pcap=PcapFile.all().filter('filekey =', filekey).get()
    if pcap:
      self.response.headers['Content-Disposition']=str("attachment; filename=\"%s\"" % (pcap.filename))

      resource = str(urllib.unquote(filekey))
      blob_info = blobstore.BlobInfo.get(resource)
      self.send_blob(blob_info)

class DownloadReport(JsonPage):
  def processJson(self, method, user, req, resp, args, obj):
    user = users.get_current_user()

    if not user:
      return None

    protocolName=self.request.get('protocol')
    datasetName=self.request.get('dataset')

    service=ReportService()
    result=service.json_getForDatasetAndProtocol(datasetName, protocolName)
    return result

class DownloadModel(JsonPage):
  def processJson(self, method, user, req, resp, args, obj):
    user = users.get_current_user()

    if not user:
      return None

    protocolName=self.request.get('protocol')
    datasetName=self.request.get('dataset')

    service=ReportService()
    result=service.json_getModel(datasetName, protocolName)
    return result

class Report(TemplatePage):
  def processContext(self, method, user, req, resp, args, context):
    filekey=self.request.get('filekey')
    context['userid']=user.email().lower()

    pcap=PcapFile.all().filter("filekey =", filekey).get()
    if pcap:
      context['pcap']=pcap

      if pcap.report and pcap.report.incoming and pcap.report.outgoing:
        context['report']=dumps({
          'incoming': {
            'lengths': map(int, pcap.report.incoming.lengths),
            'entropy': pcap.report.incoming.entropies
          },
          'outgoing': {
            'lengths': map(int, pcap.report.outgoing.lengths),
            'entropy': pcap.report.outgoing.entropies
          }
        })
    logging.info('pcap: '+str(pcap))

  def requireLogin(self):
    return True

class ProtocolReport(TemplatePage):
  def processContext(self, method, user, req, resp, args, context):
    name=self.request.get('protocol')
    context['userid']=user.email().lower()

    context['protocol']=None
    context['report']=None

    protocol=Protocol.all().filter('creator =', user).filter('name =', name).get()
    if protocol:
      context['protocol']=protocol
      logging.info('protocol: '+str(protocol))
      pcaps=PcapFile.all().filter('protocol =', protocol).run()
      if pcaps:
        context['report']=dumps({
          'incoming': {
            'lengths': self.compileIncomingLengths(pcaps),
            'entropy': self.compileIncomingEntropy(pcaps)
          },
          'outgoing': {
            'lengths': self.compileOutgoingLengths(pcaps),
            'entropy': self.compileOutgoingEntropy(pcaps)
          }
        })

  def compileIncomingLengths(self, pcaps):
    lengths=[0]*1500
    for pcap in pcaps:
      if pcap.report and pcap.report.incoming:
        for x in range(len(pcap.report.incoming.lengths)):
          lengths[x]=lengths[x]+pcap.report.incoming.lengths[x]
    return lengths

  def compileOutgoingLengths(self, pcaps):
    lengths=[0]*1500
    for pcap in pcaps:
      if pcap.report and pcap.report.outgoing:
        for x in range(len(pcap.report.outgoing.lengths)):
          lengths[x]=lengths[x]+pcap.report.outgoing.lengths[x]
    return lengths

  def compileIncomingEntropy(self, pcaps):
    entropies=[]
    for pcap in pcaps:
      if pcap.report and pcap.report.incoming:
        entropies=entropies+pcap.report.incoming.entropies
    entropies=filter(lambda x: x!=0, entropies)
    entropies.sort()
    return entropies

  def compileOutgoingEntropy(self, pcaps):
    entropies=[]
    for pcap in pcaps:
      if pcap.report and pcap.report.outgoing:
        entropies=entropies+pcap.report.incoming.entropies
    entropies=filter(lambda x: x!=0, entropies)
    entropies.sort()
    return entropies

  def requireLogin(self):
    return True

class DatasetIndex(TemplatePage):
  def processContext(self, method, user, req, resp, args, context):
    logging.debug("dataset index")
    name=self.request.get('dataset')
    context['userid']=user.email().lower()
    context['dataset']=name

    context['pcaps']=None
    context['prots']=None

    dataset=Dataset.all().filter('creator =', user).filter('name =', name).get()
    if dataset:
      context['dataset']=dataset
      logging.info('dataset: '+str(dataset))

      pcaps=PcapFile.all().filter("uploader =", user).filter('dataset =', dataset).order('filename').run()
      context['pcaps']=pcaps
      logging.info('pcaps: '+str(pcaps))

      prots=Protocol.all().filter("creator =", user).order('name').run()
      context['prots']=prots
      logging.info('prots: '+str(prots))

  def requireLogin(self):
    return True

class DatasetReport(TemplatePage):
  def processContext(self, method, user, req, resp, args, context):
    protocolName=self.request.get('protocol')
    datasetName=self.request.get('dataset')
    context['userid']=user.email().lower()

    context['protocol']=None
    context['dataset']=None
    context['report']=None

    protocol=Protocol.all().filter('creator =', user).filter('name =', protocolName).get()
    if protocol:
      context['protocol']=protocol
      logging.info('protocol: '+str(protocol))

      dataset=Dataset.all().filter('creator =', user).filter('name =', datasetName).get()
      if dataset:
        context['dataset']=dataset
        logging.info('dataset: '+str(dataset))

        pcaps=PcapFile.all().filter("uploader =", user).filter('protocol =', protocol).filter('dataset =', dataset).run()
        if pcaps:
          logging.info("Found %d pcaps" %(len(pcaps)))
          context['report']=dumps({
            'incoming': {
              'lengths': self.compileIncomingLengths(pcaps),
              'entropy': self.compileIncomingEntropy(pcaps)
            },
            'outgoing': {
              'lengths': self.compileOutgoingLengths(pcaps),
              'entropy': self.compileOutgoingEntropy(pcaps)
            }
          })

  def compileIncomingLengths(self, pcaps):
    lengths=[0]*1500
    for pcap in pcaps:
      if pcap.report and pcap.report.incoming:
        for x in range(len(pcap.report.incoming.lengths)):
          lengths[x]=lengths[x]+pcap.report.incoming.lengths[x]
    return lengths

  def compileOutgoingLengths(self, pcaps):
    lengths=[0]*1500
    for pcap in pcaps:
      if pcap.report and pcap.report.outgoing:
        for x in range(len(pcap.report.outgoing.lengths)):
          lengths[x]=lengths[x]+pcap.report.outgoing.lengths[x]
    return lengths

  def compileIncomingEntropy(self, pcaps):
    entropies=[]
    for pcap in pcaps:
      if pcap.report and pcap.report.incoming:
        entropies=entropies+pcap.report.incoming.entropies
    entropies=filter(lambda x: x!=0, entropies)
    entropies.sort()
    return entropies

  def compileOutgoingEntropy(self, pcaps):
    entropies=[]
    for pcap in pcaps:
      if pcap.report and pcap.report.outgoing:
        entropies=entropies+pcap.report.incoming.entropies
    entropies=filter(lambda x: x!=0, entropies)
    entropies.sort()
    return entropies

  def requireLogin(self):
    return True

class UploadReport(JsonPage):
  def processJson(self, method, user, req, resp, args, obj):
    filekey=obj['filekey']
    logging.info('UploadReport: '+str(obj))

    pcap=PcapFile.all().filter("filekey =", filekey).get()
    pcap.status=status.complete
    pcap.report=json.dumps(obj)
    pcap.save()

    print('Uploaded report for '+str(pcap))

    return None

  def requireLogin(self):
    return True

class ForceProcess(JsonPage):
  def processJson(self, method, user, req, resp, args, obj):
    filekey=obj['filekey']

    deferred.defer(processPcap, filekey)
