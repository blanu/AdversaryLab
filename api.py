import logging

from google.appengine.api import users
from google.appengine.api import memcache
from google.appengine.ext import db
from google.appengine.ext import deferred

from rpc import JsonRpcService
from models import *
from probmodels import *
from processModel import generateModel

def compileLengths(stream, result):
  lengths=result['lengths']
  for x in range(len(stream.lengths)):
    lengths[x]=lengths[x]+stream.lengths[x]
  result['lengths']=lengths
  return result

def compileContent(packets, result):
  content=packets['content']
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
    prots=Protocol.all().filter("creator =", user).run()
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
    prots=Dataset.all().filter("creator =", user).run()
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
    pcaps=PcapFile.all().filter("uploader =", user).run()
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
  result=compileLengths(stream, result)
  result=compileContent(stream, result)
  result=compileEntropy(stream, result)
  return result

def emptyResult(filename):
  return {
    'filename': filename,
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

class ProtocolStatInfo:
  def __init__(self):
    self.sizes=[0]*1500
    self.content=[0]*256
    self.durations=[]
    self.entropies=[]
    self.flow=[]

def combineProtocol(pcaps):
  ipstat=ProtocolStatInfo()
  opstat=ProtocolStatInfo()
  for pcap in pcaps:
    for x in range(1500):
      ipstat.sizes[x]=ipstat.sizes[x]+pcap.incomingStats.lengths[x]
      opstat.sizes[x]=opstat.sizes[x]+pcap.outgoingStats.lengths[x]
    for x in range(256):
      ipstat.content[x]=ipstat.content[x]+pcap.incomingStats.content[x]
      opstat.content[x]=opstat.content[x]+pcap.outgoingStats.content[x]
    for d in pcap.incomingStats.durations:
      ipstat.durations.append(d)
    for d in pcap.outgoingStats.durations:
      opstat.durations.append(d)
    for e in pcap.incomingStats.entropies:
      ipstat.entropies.append(e)
    for e in pcap.outgoingStats.entropies:
      opstat.entropies.append(e)
    for count in pcap.incomingStats.flow:
      ipstat.flow.append(count)
    for count in pcap.outgoingStats.flow:
      opstat.flow.append(count)
  return ipstat, opstat

class ReportService(JsonRpcService):
  def json_getForPcap(self, filekey):
    sort=False
    user = users.get_current_user()
    logging.info('ACTION(Report): getForPcap(%s, %s)' % (user, filekey))

    if not user:
      logging.error('User not logged in')
      return None

    pcap=PcapFile.all().filter("uploader =", user).filter("filekey =", filekey).get()
    if pcap and pcap.incomingStats and pcap.outgoingStats:
      if sort:
        return {
          'filename': pcap.filename,
          'incoming': {
            'lengths': sorted(pcap.incomingStats.lengths),
            'content': sorted(pcap.incomingStats.content),
            'entropy': sorted(pcap.incomingStats.entropies),
            'durations': sorted(pcap.incomingStats.durations),
            'flow': sorted(pcap.incomingStats.flow)
          },
          'outgoing': {
            'lengths': sorted(pcap.outgoingStats.lengths),
            'content': sorted(pcap.outgoingStats.content),
            'entropy': sorted(pcap.outgoingStats.entropies),
            'durations': sorted(pcap.outgoingStats.durations),
            'flow': sorted(pcap.outgoingStats.flow)
          }
        }
      else:
        return {
          'filename': pcap.filename,
          'incoming': {
            'lengths': pcap.incomingStats.lengths,
            'content': pcap.incomingStats.content,
            'entropy': pcap.incomingStats.entropies,
            'durations': pcap.incomingStats.durations,
            'flow': pcap.incomingStats.flow
          },
          'outgoing': {
            'lengths': pcap.outgoingStats.lengths,
            'content': pcap.outgoingStats.content,
            'entropy': pcap.outgoingStats.entropies,
            'durations': pcap.outgoingStats.durations,
            'flow': pcap.outgoingStats.flow
          }
        }
    else:
      logging.error('Pcap or stats were null %s %s %s' % (pcap, pcap.incomingStats, pcap.outgoingStats))
      return None

  def json_getForProtocol(self, protocolName):
    sort=True
    logging.info('ACTION(Report): getForProtocol')
    user = users.get_current_user()

    if not user:
      return None

    protocol=Protocol.all().filter('creator =', user).filter('name =', protocolName).get()
    if protocol:
      pcaps=PcapFile.all().filter('uploader =', user).filter('protocol =', protocol).run()
      if pcaps:
        ipstat, opstat=combineProtocol(pcaps)
        if sort:
          return {
            'filename': protocolName,
            'incoming': {
              'lengths': sorted(ipstat.sizes),
              'content': sorted(ipstat.content),
              'entropy': sorted(ipstat.entropies),
              'durations': sorted(ipstat.durations),
              'flow': sorted(ipstat.flow)
            },
            'outgoing': {
              'lengths': sorted(opstat.sizes),
              'content': sorted(opstat.content),
              'entropy': sorted(opstat.entropies),
              'durations': sorted(opstat.durations),
              'flow': sorted(opstat.flow)
            }
          }
        else:
          return {
            'filename': protocolName,
            'incoming': {
              'lengths': ipstat.sizes,
              'content': ipstat.content,
              'entropy': ipstat.entropies,
              'durations': ipstat.durations,
              'flow': ipstat.flow
            },
            'outgoing': {
              'lengths': opstat.sizes,
              'content': opstat.content,
              'entropy': opstat.entropies,
              'durations': opstat.durations,
              'flow': opstat.flow
            }
          }
      else:
        logging.error('Pcap or stats were null %s %s %s' % (pcap, pcap.incomingStats, pcap.outgoingStats))
        return None

  def json_getForDatasetAndProtocol(self, datasetName, protocolName):
    sort=False
    logging.info('ACTION(Report): getForDataset')
    user = users.get_current_user()

    if not user:
      return None

    result=emptyResult(datasetName+' / '+protocolName)

    dataset=Dataset.all().filter('creator =', user).filter('name =', datasetName).get()
    if dataset:
      protocol=Protocol.all().filter('creator =', user).filter('name =', protocolName).get()
      if protocol:
        pcaps=PcapFile.all().filter('uploader =', user).filter('dataset =', dataset).filter('protocol =', protocol).run()
        if pcaps:
          ipstat, opstat=combineProtocol(pcaps)
          if sort:
            return {
              'filename': datasetName +" / "+protocolName,
              'incoming': {
                'lengths': sorted(ipstat.sizes),
                'content': sorted(ipstat.content),
                'entropy': sorted(ipstat.entropies),
                'durations': sorted(ipstat.durations),
                'flow': sorted(ipstat.flow)
              },
              'outgoing': {
                'lengths': sorted(opstat.sizes),
                'content': sorted(opstat.content),
                'entropy': sorted(opstat.entropies),
                'durations': sorted(opstat.durations),
                'flow': sorted(opstat.flow)
              }
            }
          else:
            return {
              'filename': protocolName,
              'incoming': {
                'lengths': ipstat.sizes,
                'content': ipstat.content,
                'entropy': ipstat.entropies,
                'durations': ipstat.durations,
                'flow': ipstat.flow
              },
              'outgoing': {
                'lengths': opstat.sizes,
                'content': opstat.content,
                'entropy': opstat.entropies,
                'durations': opstat.durations,
                'flow': opstat.flow
              }
            }
        else:
          logging.error('Pcap or stats were null %s %s %s' % (pcap, pcap.incomingStats, pcap.outgoingStats))
          return None

  def json_generateModel(self, datasetName, protocolName):
    logging.info('ACTION(Report): generateModel')
    user = users.get_current_user()

    if not user:
      return None

    result=None

    dataset=Dataset.all().filter('creator =', user).filter('name =', datasetName).get()
    if dataset:
      protocol=Protocol.all().filter('creator =', user).filter('name =', protocolName).get()
      if protocol:
        pcaps=PcapFile.all().filter('uploader =', user).filter('dataset =', dataset).filter('protocol =', protocol).run()
        if pcaps:
          ipstat, opstat=combineProtocol(pcaps)
          deferred.defer(generateModel, user, protocol, dataset, ipstat, opstat)
          return True

    return False

  def json_getModel(self, datasetName, protocolName):
    logging.info('ACTION(Report): getModel')
    user = users.get_current_user()

    if not user:
      return None

    result=None

    dataset=Dataset.all().filter('creator =', user).filter('name =', datasetName).get()
    if dataset:
      protocol=Protocol.all().filter('creator =', user).filter('name =', protocolName).get()
      if protocol:
        incomingModel=ProtocolModel.all().filter('dataset =', dataset).filter('protocol =', protocol).filter('outgoing', False).get()
        outgoingModel=ProtocolModel.all().filter('dataset =', dataset).filter('protocol =', protocol).filter('outgoing', True).get()
        logging.debug('Models')
        logging.debug(incomingModel)
        logging.debug(outgoingModel)
        if incomingModel and outgoingModel:
          return {
            'incoming': {
              'length': [incomingModel.length.distribution.mean, incomingModel.length.distribution.sd],
              'entropy': [incomingModel.entropy.distribution.mean, incomingModel.entropy.distribution.sd],
              'flow': incomingModel.flow.distribution.parameter,
              'content': incomingModel.content.distribution.distribution,
              'duration': incomingModel.duration.distribution.parameter
            },
            'outgoing': {
              'length': [outgoingModel.length.distribution.mean, outgoingModel.length.distribution.sd],
              'entropy': [outgoingModel.entropy.distribution.mean, outgoingModel.entropy.distribution.sd],
              'flow': outgoingModel.flow.distribution.parameter,
              'content': outgoingModel.content.distribution.distribution,
              'duration': outgoingModel.duration.distribution.parameter
            }
          }

    return False
