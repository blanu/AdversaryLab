import logging

from google.appengine.api import users
from google.appengine.api import memcache
from google.appengine.ext import db

from rpc import JsonRpcService
from models import *

class ProtocolService(JsonRpcService):
  def json_add(self, protocol):
    logging.info('ACTION(Protocol): add')
    user = users.get_current_user()
    logging.info('rpc user '+str(user))

    prot=Protocol.all().filter("creator =", user).filter("name =", protocol).get()
    if prot:
      return False
    else:
      prot=Protocol(creator=user, name=protocol)
      prot.save()
      return True

  def json_delete(self, protocol):
    logging.info('ACTION(Protocol): delete')
    user = users.get_current_user()

    prot=Protocol.all().filter("creator =", user).filter("name =", protocol).get()
    if prot:
      prot.delete()
      return True
    else:
      return False

  def json_list(self):
    logging.info('ACTION(Protocol): list')
    user = users.get_current_user()

    results=[]
    prots=Protocol.all().filter("creator =", user).fetch(100)
    for prot in prots:
      results.append(prot.name)
    return results

class DatasetService(JsonRpcService):
  def json_add(self, protocol):
    logging.info('ACTION(Dataset): add')
    user = users.get_current_user()
    logging.info('rpc user '+str(user))

    prot=Dataset.all().filter("creator =", user).filter("name =", protocol).get()
    if prot:
      return False
    else:
      prot=Dataset(creator=user, name=protocol)
      prot.save()
      return True

  def json_delete(self, protocol):
    logging.info('ACTION(Dataset): delete')
    user = users.get_current_user()

    prot=Dataset.all().filter("creator =", user).filter("name =", protocol).get()
    if prot:
      prot.delete()
      return True
    else:
      return False

  def json_list(self):
    logging.info('ACTION(Dataset): list')
    user = users.get_current_user()

    results=[]
    prots=Dataset.all().filter("creator =", user).fetch(100)
    for prot in prots:
      results.append(prot.name)
    return results

class PcapService(JsonRpcService):
  def json_delete(self, filekey):
    logging.info('ACTION(Pcap): delete')
    user = users.get_current_user()

    pcap=PcapFile.all().filter("uploader =", user).filter("filekey =", filekey).get()
    if pcap:
      pcap.delete()
      return True
    else:
      return False

  def json_list(self):
    logging.info('ACTION(Pcap): list')
    user = users.get_current_user()

    results=[]
    pcaps=PcapFile.all().filter("uploader =", user).fetch(100)
    for pcap in pcaps:
      results.append({'name': pcap.name, 'filekey': pcap.filekey, 'status': pcap.status})
    return results

  def json_setProtocol(self, filekey, protocol):
    logging.info('ACTION(Pcap): setProtocol')
    user = users.get_current_user()

    pcap=PcapFile.all().filter("uploader =", user).filter("filekey =", filekey).get()
    protocol=Protocol.all().filter('creator =', user).filter('name =', protocol).get()
    if pcap and protocol:
      pcap.protocol=protocol
      pcap.save()
      return True
    else:
      return False

  def json_setDataset(self, filekey, datasetName):
    logging.info('ACTION(Pcap): setDataset')
    user = users.get_current_user()

    pcap=PcapFile.all().filter("uploader =", user).filter("filekey =", filekey).get()
    dataset=Dataset.all().filter('creator =', user).filter('name =', datasetName).get()
    if pcap and dataset:
      pcap.dataset=dataset
      pcap.save()
      return True
    else:
      return False

    def json_uploadCode(self):
      return blobstore.create_upload_url('/upload')
