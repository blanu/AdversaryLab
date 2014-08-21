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
  return u

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

def splitStreams(tracefile, streamdir):
  packets=rdpcap(tracefile)
  streams={}

class CaptureStats:
  def __init__(self, pcap, port):
    self.pcap=pcap
    self.port=port

  def processPcap(self, streamfile):
    packets=rdpcap(streamfile)

    for packet in packets:
      logging.debug("packet: "+str(packet))
      ports=getPorts(packet)
      if ports:
        conn=self.getConnection(ports)
        stream=Stream.get_or_insert(connection=conn, srcPort=sport, dstPort=dport)
        self.processPacket(stream, packet)

  def getConnection(self, ports):
    sport, dport=ports
    if sport==self.port:
      conn=self.fetchConnection(dport, self.port)
    elif dport==self.port:
      conn=self.fetchConnection(sport, self.port)
    else:
      logging.error("Unknown ports %d/%d, expecting %d" % (sport, dport, self.port))

  def fetchConnection(self, incomingPort, outgoingPort):
    return Connection.get_or_insert(outgoingPort=outgoingPort, incomingPort=incomingPort)

  def processPacket(self, stream, packet):
    length=0
    counts=[0]*256

    if 'IP' in packet:
      try:
        length=packet['IP'].fields['len']
      except:
        logging.error('IP packet has no length')
        return
    elif 'IPv6' in packet:
      try:
        length=packet['IPv6'].fields['len']
      except:
        logging.error('IPv6 packet has no length')
        return
    else:
      logging.error('Non-IP packet: '+str(packet))
      return

    if 'Raw' in packet:
      contents=bytes(packet['Raw'])
      total=len(contents)
      logging.info("found %d bytes" % (len(contents)))

      for c in contents:
        x=ord(c)
        counts[x]=counts[x]+1

    p=Packet(stream=stream, length=length, entropy=calculateEntropy(counts), content=counts, timestamp=int(packet.time))
    p.save()

  def compileSide(self, selector):
    lengths=[0]*1500
    entropies=[]
    counts=[0]*256
    bps=[]
    for sid in self.streams.keys():
      stream=self.streams[sid]
      ls, e, cs, bs=stream.compile()[selector]
      for x in range(len(ls)):
        lengths[x]=lengths[x]+ls[x]
      if e!=0:
        entropies.append(e)
      for x in range(len(cs)):
        counts[x]=counts[x]+cs[x]
      bps.append(bs)
    stats=PcapStats(lengths=lengths, entropies=entropies, content=counts, bps=bps)
    stats.save()
    return stats

  def compileStream(self):
    volume=[]
    direction=[]
    directedVolume=[]

    for sid in self.streams.keys():
      stream=self.streams[sid]
      vs, ds, dvs=stream.compile()[3]
      volume.append()
      direction.append()
    stats=PcapStreamStats(volume=volume, direction=direction, directedVolume=directedVolume)
    stats.save()
    return stats

class StreamStats:
  def __init__(self, connid, port):
    self.id=connid
    self.port=port
    self.startTime=0

    self.incoming=SideStats()
    self.outgoing=SideStats()

  def processPacket(self, packet):
    ports=getPorts(packet)
    if ports:
      sport, dport=ports
      if self.startTime==0:
        self.startTime=int(packet.time)
        self.incoming.setStartTime(self.startTime)
        self.outgoing.setStartTime(self.startTime)
      if sport==self.port:
        self.incoming.processPacket(packet)
      elif dport==self.port:
        self.outgoing.processPacket(packet)
      else:
        logging.error("Unknown ports %d/%d, expecting %d" % (sport, dport, self.port))

  def compile(self):
    i=self.incoming.compile()
    o=self.outgoing.compile()
    return (i, o, self.compileBps(i, o))

  def compileBps(self, is, os):
    volume=[]
    direction=[]
    directedVolume=[]

    for (i, o) in zip(ios, os):
      volume.append(i+o)
      directedVolume.append(i-o)
      if i==0 and o==0:
        direction.append(0)
      elif i==0:
        direction.append(1)
      elif o==0:
        direction.append(-1)
      else:
        avg=float(i)/float(i+o)
        direction.append((avg-0.5)*2)

    return (volume, direction, directedVolume)

class SideStats:
  def __init__(self):
    self.startTime=0
    self.currentTime=0
    self.currentBps=0

    self.lengths=[0]*1500
    self.total=0
    self.counts=[0]*256
    self.bps=[]

  def setStartTime(self, st):
    self.startTime=st
    self.currentTime=self.startTime

  def processPacket(self, packet):
    if 'IP' in packet:
      try:
        l=packet['IP'].fields['len']
        if l<len(self.lengths):
          self.lengths[l]=self.lengths[l]+1
          logging.info("packet of length %d" % (l))
          self.addBps(int(packet.time), l)
        else:
          logging.error("Packet length too big: %d" % (l))
      except:
        logging.error('IP packet has no length')
        return
    elif 'IPv6' in packet:
      try:
        l=packet['IPv6'].fields['len']
        if l<len(self.lengths):
          self.lengths[l]=self.lengths[l]+1
          logging.info("packet of length %d" % (l))
          self.addBps(int(packet.time), l)
        else:
          logging.error("Packet length too big: %d" % (l))
      except:
        logging.error('IPv6 packet has no length')
        return
    else:
      logging.error('Non-IP packet: '+str(packet))
      return

    if 'Raw' in packet:
      contents=bytes(packet['Raw'])
      self.total=self.total+len(contents)
      logging.info("found %d bytes" % (len(contents)))

      for c in contents:
        x=ord(c)
        self.counts[x]=self.counts[x]+1

  def addBps(self, time, length):
    if time==self.currentTime:
      self.currentBps=self.currentBps+length
    elif time>self.currentTime:
      self.bps.append(self.currentBps)

      gap=time-self.currentTime
      for index in range(gap)-1:
        self.bps.append(0)

      self.currentBps=0
      self.currentTime=time
    else:
      logging.error('Time moving backwords: %d %d' % (time, self.currentTime))

  def compile(self):
    u=0
    for count in self.counts:
      if self.total==0:
        p=0
      else:
        p=float(count)/float(self.total)
      if p==0:
        e=0
      else:
        e=-p*math.log(p, 2)
        logging.error('entropy: '+str(e))
      u=u+e

    return (self.lengths, float(u), self.counts, self.bps)

def processPcap(blobkey):
  blob_info=blobstore.get(blobkey)
  logging.info("processing "+blob_info.filename)

  pcap=PcapFile.all().filter("filekey =", blobkey).get()
  pcap.status=status.processing
  pcap.save()

  generateReport(pcap)

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
