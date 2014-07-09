import math
import logging

from google.appengine.api import urlfetch
from google.appengine.ext import db
from google.appengine.ext import blobstore

from scapy.all import sniff, IPv6, IP, UDP, TCP, rdpcap, wrpcap

import status
from models import *

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
  def __init__(self, port):
    self.port=port

    self.streams={}

  def processStream(self, streamfile):
    packets=rdpcap(streamfile)

    for packet in packets:
      logging.debug("packet: "+str(packet))
      sid=streamId(packet)

      if sid:
        if sid in self.streams.keys():
          stream=self.streams[sid]
          stream.processPacket(packet)
        else:
          stream=StreamStats(sid, self.port)
          stream.processPacket(packet)
          self.streams[sid]=stream

  def compile(self):
    stats=PcapReport()
    stats.incoming=self.compileSide(0)
    stats.outgoing=self.compileSide(1)
    stats.save()
    return stats

  def compileSide(self, selector):
    lengths=[0]*1500
    entropies=[]
    for sid in self.streams.keys():
      stream=self.streams[sid]
      ls, e=stream.compile()[selector]
      for x in range(len(ls)):
        lengths[x]=lengths[x]+ls[x]
      if e!=0:
        entropies.append(e)
    stats=PcapStats(lengths=lengths, entropies=entropies)
    stats.save()
    return stats

class StreamStats:
  def __init__(self, connid, port):
    self.id=connid
    self.port=port

    self.incoming=SideStats()
    self.outgoing=SideStats()

  def processPacket(self, packet):
    ports=getPorts(packet)
    if ports:
      sport, dport=ports
      if sport==self.port:
        self.incoming.processPacket(packet)
      elif dport==self.port:
        self.outgoing.processPacket(packet)
      else:
        logging.error("Unknown ports %d/%d, expecting %d" % (sport, dport, self.port))

  def compile(self):
    return (self.incoming.compile(), self.outgoing.compile())

class SideStats:
  def __init__(self):
    self.lengths=[0]*1500
    self.total=0
    self.counts=[0]*256

  def processPacket(self, packet):
    if 'IP' in packet:
      try:
        l=packet['IP'].fields['len']
        if l<len(self.lengths):
          self.lengths[l]=self.lengths[l]+1
          logging.info("packet of length %d" % (l))
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

    return (self.lengths, float(u))

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

  report=createReport(pcapfilename, pcap.port)
  if report:
    replaceReport(pcap, report)
    pcap.status=status.complete
    pcap.save()

def replaceReport(pcap, report):
  if pcap.report:
    if pcap.report.incoming:
      pcap.report.incoming.delete()
    if pcap.report.outgoing:
      pcap.report.outgoing.delete()
    pcap.report.delete()
  pcap.report=report

def pump(inputf, outputf):
  buffsize=4096
  data=inputf.read(buffsize)
  while data!=None and len(data)!=0:
    outputf.write(data)
    data=inputf.read(buffsize)

def createReport(pcapfilename, port):
  stats=CaptureStats(port)
  stats.processStream(pcapfilename)
  return stats.compile()
