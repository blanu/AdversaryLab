import logging

from google.appengine.api import users
from google.appengine.api import memcache
from google.appengine.ext import db

from rpc import JsonRpcService
from models import *

def compileLengths(packets, result):
  lengths=result['lengths']
  for packet in packets:
    lengths[packet.length]=lengths[packet.length]+1
    length=length+packet.length
  result['lengths']=lengths
  return result

def compileContent(packets, result):
  content=packets['content']
  for packet in packets:
    for x in range(len(packet.content)):
      content[x]=content[x]+packet.content[x]
  result['content']=content
  return result

def calculateEntropy(contents):
  total=sum(contents)

  u=0
  for count in contents:
    if total==0:
      p=0
    else:
      p=float(count)/float(total)
    if p==0:
      e=0
    else:
      e=-p*math.log(p, 2)
    u=u+e
  return u

def compileEntropy(packets, result):
  entropies=packets['entropy']
  for packet in packets:
    entropy=calculateEntropy(packet.content)
    if entropy!=0:
      entropies.append(entropy)
  entropies.sort()

  result['entropy']=entropies
  return result

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

def compileStream(stream, result):
  packets=Packet.all().filter("stream =", stream).fetch(100)
  result=compileLengths(packets, result)
  result=compileContent(packets, result)
  result=compileEntropy(packets, result)
  return result

def emptyResult():
  return {
    'filename': pcap.filename,
    'incoming': {
      'lengths': [0]*1400,
      'content': [0]*256,
      'entropies': []
    },
    'outgoing': {
      'lengths': [0]*1400,
      'content': [0]*256,
      'entropies': []
    }
  }

class ReportService(JsonRpcService):
  def json_getForPcap(self, filekey):
    logging.info('ACTION(Report): getForPcap')
    user = users.get_current_user()

    if not user:
      return None

    pcap=PcapFile.all().filter("uploader =", user).filter("filekey =", filekey).get()
    result=emptyResult()

    if pcap:
      conns=Connection.().filter("pcap =", pcap).fetch(100)
      for conn in conns:
        streams=Stream.all().filter("connection =", conn).fetch(100)
        if conn.incomingPort==pcap.port:
          for stream in streams:
            result['incoming']=compileStream(stream, result['incoming'])
        elif conn.outgoingPort==pcap.port:
          for stream in streams:
            result['outgoing']=compileStream(stream, result['outgoing'])
        else:
          logging.error("Connection has no matching port")

    return result

  def json_getForProtocol(self, protocolName):
    logging.info('ACTION(Report): getForProtocol')
    user = users.get_current_user()

    if not user:
      return None

    result=emptyResult()

    protocol=Protocol.all().filter('creator =', user).filter('name =', protocolName).get()
    if protocol:
      pcaps=PcapFile.all().filter('uploader =', user).filter('protocol =', protocol).fetch(100)
      if pcaps:
        logging.info("Found %d pcaps" %(len(pcaps)))

        for pcap in pcaps:
          conns=Connection.().filter("pcap =", pcap).fetch(100)
          for conn in conns:
            streams=Stream.all().filter("connection =", conn).fetch(100)
            if conn.incomingPort==pcap.port:
              for stream in streams:
                result['incoming']=compileStream(stream, result['incoming'])
            elif conn.outgoingPort==pcap.port:
              for stream in streams:
                result['outgoing']=compileStream(stream, result['outgoing'])
            else:
              logging.error("Connection has no matching port")

    return result

  def json_getForDatasetAndProtocol(self, datasetName, protocolName):
    logging.info('ACTION(Report): getForDataset')
    user = users.get_current_user()

    if not user:
      return None

    result=emptyResult()

    dataset=Dataset.all().filter('creator =', user).filter('name =', datasetName).get()
    if dataset:
      protocol=Protocol.all().filter('creator =', user).filter('name =', protocolName).get()
      if protocol:
        pcaps=PcapFile.all().filter('uploader =', user).filter('dataset =', dataset).filter('protocol =', protocol).fetch(100)
        if pcaps:
          logging.info("Found %d pcaps" %(len(pcaps)))

          for pcap in pcaps:
            conns=Connection.().filter("pcap =", pcap).fetch(100)
            for conn in conns:
              streams=Stream.all().filter("connection =", conn).fetch(100)
              if conn.incomingPort==pcap.port:
                for stream in streams:
                  result['incoming']=compileStream(stream, result['incoming'])
              elif conn.outgoingPort==pcap.port:
                for stream in streams:
                  result['outgoing']=compileStream(stream, result['outgoing'])
              else:
                logging.error("Connection has no matching port")

    return result
