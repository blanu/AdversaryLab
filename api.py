import logging

from google.appengine.api import users
from google.appengine.api import memcache
from google.appengine.ext import db

from rpc import JsonRpcService
from models import *

def compileIncomingLengths(pcaps):
  lengths=[0]*1500
  for pcap in pcaps:
    if pcap.report and pcap.report.incoming:
      for x in range(len(pcap.report.incoming.lengths)):
        lengths[x]=lengths[x]+pcap.report.incoming.lengths[x]
  return lengths

def compileOutgoingLengths(pcaps):
  lengths=[0]*1500
  for pcap in pcaps:
    if pcap.report and pcap.report.outgoing:
      for x in range(len(pcap.report.outgoing.lengths)):
        lengths[x]=lengths[x]+pcap.report.outgoing.lengths[x]
  return lengths

def compileIncomingEntropy(pcaps):
  entropies=[]
  for pcap in pcaps:
    if pcap.report and pcap.report.incoming:
      entropies=entropies+pcap.report.incoming.entropies
  entropies=filter(lambda x: x!=0, entropies)
  entropies.sort()
  return entropies

def compileOutgoingEntropy(pcaps):
  entropies=[]
  for pcap in pcaps:
    if pcap.report and pcap.report.outgoing:
      entropies=entropies+pcap.report.incoming.entropies
  entropies=filter(lambda x: x!=0, entropies)
  entropies.sort()
  return entropies

def compileIncomingContent(pcaps):
  content=[0]*256
  for pcap in pcaps:
    if pcap.report and pcap.report.incoming:
      for x in range(len(pcap.report.incoming.content)):
        content[x]=content[x]+pcap.report.incoming.content[x]
  return content

def compileOutgoingContent(pcaps):
  content=[0]*256
  for pcap in pcaps:
    if pcap.report and pcap.report.outgoing:
      for x in range(len(pcap.report.outgoing.content)):
        content[x]=content[x]+pcap.report.outgoing.content[x]
  return content

def compileIncomingBps(pcaps):
  bps=[]
  for pcap in pcaps:
    if pcap.report and pcap.report.incoming:
      bps.append(pcap.report.incoming.bps)
  return bps

def compileOutgoingBps(pcaps):
  bps=[]
  for pcap in pcaps:
    if pcap.report and pcap.report.outgoing:
      bps.append(pcap.report.incoming.bps)
  return bps

class UserService(JsonRpcService):
  def json_isLoggedIn(self):
    user = users.get_current_user()
    logging.info('isLoggedIn '+str(user));
    return user!=None

  def json_isAdmin(self):
    return users.is_current_user_admin()

  def json_login(self):
    return users.create_login_url('/')

  def json_logout(self):
    return users.create_logout_url('/')

class ProtocolService(JsonRpcService):
  def json_add(self, protocol):
    logging.info('ACTION(Protocol): add')
    user = users.get_current_user()
    logging.info('rpc user '+str(user))

    if not user:
      return None

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

    if not user:
      return None

    prot=Protocol.all().filter("creator =", user).filter("name =", protocol).get()
    if prot:
      prot.delete()
      return True
    else:
      return False

  def json_list(self):
    logging.info('ACTION(Protocol): list')
    user = users.get_current_user()

    if not user:
      return None

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

    if not user:
      return None

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

    if not user:
      return None

    prot=Dataset.all().filter("creator =", user).filter("name =", protocol).get()
    if prot:
      prot.delete()
      return True
    else:
      return False

  def json_list(self):
    logging.info('ACTION(Dataset): list')
    user = users.get_current_user()

    if not user:
      return None

    results=[]
    prots=Dataset.all().filter("creator =", user).fetch(100)
    for prot in prots:
      results.append(prot.name)
    return results

class PcapService(JsonRpcService):
  def json_delete(self, filekey):
    logging.info('ACTION(Pcap): delete')
    user = users.get_current_user()

    if not user:
      return None

    pcap=PcapFile.all().filter("uploader =", user).filter("filekey =", filekey).get()
    if pcap:
      pcap.delete()
      return True
    else:
      return False

  def json_list(self):
    logging.info('ACTION(Pcap): list')
    user = users.get_current_user()

    if not user:
      return None

    results=[]
    pcaps=PcapFile.all().filter("uploader =", user).fetch(100)
    for pcap in pcaps:
      if pcap.dataset:
        dataset=pcap.dataset.name
      else:
        dataset=None
      if pcap.protocol:
        protocol=pcap.protocol.name
      else:
        protocol=None
      results.append({'filename': pcap.filename, 'filekey': str(pcap.filekey.key()), 'status': pcap.status, 'dataset': dataset, 'protocol': protocol})
    return results

  def json_setProtocol(self, filekey, protocol):
    logging.info('ACTION(Pcap): setProtocol')
    user = users.get_current_user()

    if not user:
      return None

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

    if not user:
      return None

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

class ReportService(JsonRpcService):
  def json_getForPcap(self, filekey):
    logging.info('ACTION(Report): getForPcap')
    user = users.get_current_user()

    if not user:
      return None

    pcap=PcapFile.all().filter("uploader =", user).filter("filekey =", filekey).get()
    if pcap and pcap.report and pcap.report.incoming and pcap.report.outgoing:
      return {
        'filename': pcap.filename,
        'incoming': {
          'lengths': map(int, pcap.report.incoming.lengths),
          'content': map(float, pcap.report.incoming.content),
          'entropy': sorted(pcap.report.incoming.entropies),
          'bps': map(int, pcap.report.incoming.bps)
        },
        'outgoing': {
          'lengths': map(int, pcap.report.outgoing.lengths),
          'content': map(float, pcap.report.incoming.content),
          'entropy': sorted(pcap.report.incoming.entropies)
          'bps': map(int, pcap.report.outgoing.bps),
        }
      }
    else:
      return None

  def json_getForProtocol(self, protocolName):
    logging.info('ACTION(Report): getForProtocol')
    user = users.get_current_user()

    if not user:
      return None

    protocol=Protocol.all().filter('creator =', user).filter('name =', protocolName).get()
    if protocol:
      pcaps=PcapFile.all().filter('uploader =', user).filter('protocol =', protocol).fetch(100)
      if pcaps:
        logging.info("Found %d pcaps" %(len(pcaps)))
        return {
          'incoming': {
            'lengths': compileIncomingLengths(pcaps),
            'content': compileIncomingContent(pcaps),
            'entropy': compileIncomingEntropy(pcaps),
            'bps': compileIncomingBps(pcaps)
          },
          'outgoing': {
            'lengths': compileOutgoingLengths(pcaps),
            'content': compileOutgoingContent(pcaps),
            'entropy': compileOutgoingEntropy(pcaps),
            'bps': compileOutgoingBps(pcaps)
          }
        }

  def json_getForDatasetAndProtocol(self, datasetName, protocolName):
    logging.info('ACTION(Report): getForDataset')
    user = users.get_current_user()

    if not user:
      return None

    dataset=Dataset.all().filter('creator =', user).filter('name =', datasetName).get()
    if dataset:
      protocol=Protocol.all().filter('creator =', user).filter('name =', protocolName).get()
      if protocol:
        pcaps=PcapFile.all().filter('uploader =', user).filter('dataset =', dataset).filter('protocol =', protocol).fetch(100)
        if pcaps:
          logging.info("Found %d pcaps" %(len(pcaps)))
          return {
            'incoming': {
              'lengths': compileIncomingLengths(pcaps),
              'content': compileIncomingContent(pcaps),
              'entropy': compileIncomingEntropy(pcaps),
              'bps': compileIncomingBps(pcaps)
            },
            'outgoing': {
              'lengths': compileOutgoingLengths(pcaps),
              'content': compileOutgoingContent(pcaps),
              'entropy': compileOutgoingEntropy(pcaps),
              'bps': compileOutgoingBps(pcaps)
            }
          }

    return None
