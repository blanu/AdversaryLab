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

    pcaps=PcapFile.all().filter("uploader =", user).order('status').fetch(10)
    context['pcaps']=pcaps
    logging.info('pcaps: '+str(pcaps))

  def requireLogin(self):
    return True

# FIXME - Does not require authentication
class Upload(blobstore_handlers.BlobstoreUploadHandler):
  def post(self):
    user = users.get_current_user()

    upload_files = self.get_uploads('pcapFile')  # 'file' is file upload field in the form
    logging.info('upload_files: '+str(upload_files))
    blob_info = upload_files[0]
    blobkey = blob_info.key()

    pcap=PcapFile(filename=blob_info.filename, uploader=user, filekey=blobkey, status=status.uploaded)
    pcap.save()

    deferred.defer(processPcap, blobkey)

    self.redirect('/dashboard')

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

class Report(TemplatePage):
  def processContext(self, method, user, req, resp, args, context):
    filekey=self.request.get('filekey')
    context['userid']=user.email().lower()

    pcap=PcapFile.all().filter("filekey =", filekey).get()
    if pcap:
      context['pcap']=pcap
    logging.info('pcap: '+str(pcap))

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
