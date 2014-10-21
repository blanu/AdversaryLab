import math
import logging

from google.appengine.api import urlfetch
from google.appengine.ext import db
from google.appengine.ext import blobstore

from scapy.all import sniff, IPv6, IP, UDP, TCP, rdpcap, wrpcap

import status
from models import *

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
  return float(u)

def streamId(packet):
  if 'IP' in packet:
    ip=packet['IP']
    src=ip.fields['src']
    dst=ip.fields['dst']
  elif 'IPv6' in packet:
    ip=packet['IPv6']
    src='['+ip.fields['src']+']'
    dst='['+ip.fields['dst']+']'
  else:
    logging.error('Non-IP packet: '+str(packet.summary()))
    return None

  if 'UDP' in packet:
    ut='udp'
    dport=packet['UDP'].fields['dport']
    sport=packet['UDP'].fields['sport']
  elif 'TCP' in packet:
    ut='tcp'
    dport=packet['TCP'].fields['dport']
    sport=packet['TCP'].fields['sport']
  else:
    logging.error('Packet not UDP or TCP: '+str(packet.summary()))
    return None

  id=ut+'_'+src+'_'+str(sport)+'_'+dst+'_'+str(dport)
  return id

def getPorts(packet):
  if 'IP' in packet or 'IPv6' in packet:
    if 'UDP' in packet:
      dport=packet['UDP'].fields['dport']
      sport=packet['UDP'].fields['sport']
      return (sport, dport)
    elif 'TCP' in packet:
      dport=packet['TCP'].fields['dport']
      sport=packet['TCP'].fields['sport']
      return (sport, dport)
  return None

# generator
def getTimestamps(packets):
  for packet in packets:
    yield int(packet.time)

# generator
def absoluteToRelative(base, timestamps):
  for timestamp in timestamps:
    yield timestamp-base

# generator
def packetsPerSecond(offsets):
  current=0
  count=0
  for offset in offsets:
    if offset==current:
      count=count+1
    else:
      yield count
      for step in range(offset-(current+1)):
        yield 0
      count=1
    current=offset

def calculateFlow(packets):
  base=int(packets[0].time)
  return packetsPerSecond(absoluteToRelative(base, getTimestamps(packets)))

class StreamStatInfo:
  def __init__(self):
    self.sizes=[0]*1500
    self.content=[0]*256
    self.timestamps=[]
    self.flow=[]

class PcapStatInfo:
  def __init__(self):
    self.sizes=[0]*1500
    self.content=[0]*256
    self.durations=[]
    self.entropies=[]
    self.flow=[]

class CaptureStats:
  def __init__(self, pcap, port):
    self.pcap=pcap
    self.port=port
    self.data={}
    self.streams={}

  def processPcap(self, streamfile):
    self.splitStreams(streamfile)
    for key in self.streams:
      packets=self.streams[key]
      info=self.data[key]
      info.flow=calculateFlow(packets)

      for packet in packets:
        self.processPacket(key, packet)

    ipstat, opstat=self.combineStreams()

    logging.info('Writing pcap stats')
    istats=Stats(lengths=ipstat.sizes, content=ipstat.content, durations=ipstat.durations, entropies=ipstat.entropies, flow=ipstat.flow)
    istats.save()
    ostats=Stats(lengths=opstat.sizes, content=opstat.content, durations=opstat.durations, entropies=opstat.entropies, flow=opstat.flow)
    ostats.save()
    self.pcap.incomingStats=istats
    self.pcap.outgoingStats=ostats
    self.pcap.save()

  def splitStreams(self, tracefile):
    packets=rdpcap(tracefile)
    for packet in packets:
      if ('IP' in packet or 'IPv6' in packet) and ('TCP' in packet or 'UDP' in packet) and 'Raw' in packet and len(packet.load)>0:
        ports=getPorts(packet)
        if ports:
          key=str(ports[0])+":"+str(ports[1])
          if key in self.streams:
            self.streams[key].append(packet)
          else:
            self.streams[key]=[packet]
          if not key in self.data:
            self.data[key]=StreamStatInfo()

  def getFirstPacketContents(self, packet):
    bs=bytes(packet.load)
    logging.debug('First packet:')
    logging.debug(packet.load)
    l=[0]*len(bs)
    for x in range(len(bs)):
      l[x]=ord(bs[x])
    return l

  def processPacket(self, stream, packet):
    info=self.data[stream]
    sz=info.sizes

    contents=bytes(packet.load)
    length=len(contents)

    if length>0 and length<1500:
      sz[length]=sz[length]+1
    else:
      logging.error('Bad length: '+str(length))

    for c in contents:
      x=ord(c)
      info.content[x]=info.content[x]+1

    info.timestamps.append(float(packet.time))

    info.sizes=sz
    self.data[stream]=info

  def combineStreams(self):
    ipstat=PcapStatInfo()
    opstat=PcapStatInfo()
    for key in self.data:
      info=self.data[key]
      srcPort, dstPort=map(int,key.split(':'))
      if srcPort==self.port:
        pstat=opstat
      elif dstPort==self.port:
        pstat=ipstat
      else:
        logging.error('Unknown port %d:%d' % (srcPort, dstPort))
        continue
      for x in range(len(info.sizes)):
        pstat.sizes[x]=pstat.sizes[x]+info.sizes[x]
      for x in range(len(info.content)):
        pstat.content[x]=pstat.content[x]+info.content[x]
      if len(info.timestamps)>1:
        pstat.durations.append(info.timestamps[-1]-info.timestamps[0])
      e=calculateEntropy(info.content)
      if e>0:
        pstat.entropies.append(e)
      for count in info.flow:
        pstat.flow.append(count)
    return ipstat, opstat

def processPcap(blobkey):
  blob_info=blobstore.get(blobkey)
  logging.info("processing "+blob_info.filename)

  pcap=PcapFile.all().filter("filekey =", blobkey).get()
  if pcap:
    pcap.status=status.processing
    pcap.save()
    generateReport(pcap)
  else:
    logging.error('Unknown pcap '+str(blobkey))
    raise Exception('Unknown pcap '+str(blobkey))

def generateReport(pcap):
  bf = pcap.filekey.open()
  pcapfilename="%s.pcap" % (pcap.filekey.key())
  f = open(pcapfilename, 'wb')
  pump(bf, f)
  bf.close()
  f.close()

  report=createReport(pcap, pcapfilename, pcap.port)
  if report:
    pcap.status=status.complete
    pcap.save()

def pump(inputf, outputf):
  buffsize=4096
  data=inputf.read(buffsize)
  while data!=None and len(data)!=0:
    outputf.write(data)
    data=inputf.read(buffsize)

def createReport(pcap, pcapfilename, port):
  stats=CaptureStats(pcap, port)
  stats.processPcap(pcapfilename)
  return True
