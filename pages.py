import re
import logging
import random
import base64
import struct
import time

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

class Upload(blobstore_handlers.BlobstoreUploadHandler):
  def post(self):
    user = users.get_current_user()

    upload_files = self.get_uploads('pcapFile')  # 'file' is file upload field in the form
    logging.info('upload_files: '+str(upload_files))
    blob_info = upload_files[0]
    blobkey = blob_info.key()

    pcap=PcapFile(filename=blob_info.filename, uploader=user, filekey=blobkey, status=status.processing)
    pcap.save()

    deferred.defer(processPcap, blobkey)

    self.redirect('/dashboard')
