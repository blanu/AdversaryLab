import math
import logging

from google.appengine.api import urlfetch
from google.appengine.ext import db
from google.appengine.ext import blobstore

import status
from models import *
from probmodels import *

def compileContent(contents):
  result=[0]*256
  for content in contents:
    for x in range(256):
      result[x]=result[x]+content[x]
  return result

def compilePosition(streams):
  bs=[0]*256
  prevs=[bs]*256
  pos=[prevs]*1440

  for stream in streams:
    content=stream.firstPacketContents
    last=ord(content[0])
    for x in range(1,max(1440,len(content))):
      current=ord(context[x])
      pos[x][last][current]=pos[x][last][current]+1
      last=current
  return pos

def generateModel(user, protocol, dataset, ipstat, opstat):
  incomingModel=ProtocolModel.all().filter('protocol =', protocol).filter('dataset =', dataset).filter('outgoing =', False).get()
  if not incomingModel:
    incomingModel=ProtocolModel(protocol=protocol, dataset=dataset, outgoing=False)
    incomingModel.save()
  if not incomingModel.length:
    incomingModel.length=fitLengthModel(ipstat.sizes)
  if not incomingModel.entropy:
    incomingModel.entropy=fitEntropyModel(ipstat.entropies)
  if not incomingModel.flow:
    incomingModel.flow=fitFlowModel(ipstat.flow)
  if not incomingModel.content:
    incomingModel.content=fitContentModel(ipstat.content)
  if not incomingModel.duration:
    incomingModel.duration=fitDurationModel(ipstat.durations)
#  createPositionModel(incomingModel, ipstat)
  incomingModel.save()

  outgoingModel=ProtocolModel.all().filter('protocol =', protocol).filter('dataset =', dataset).filter('outgoing =', True).get()
  if not outgoingModel:
    outgoingModel=ProtocolModel(protocol=protocol, dataset=dataset, outgoing=True)
    outgoingModel.save()
  if not outgoingModel.length:
    outgoingModel.length=fitLengthModel(opstat.sizes)
  if not outgoingModel.entropy:
    outgoingModel.entropy=fitEntropyModel(opstat.entropies)
  if not outgoingModel.flow:
    outgoingModel.flow=fitFlowModel(opstat.flow)
  if not outgoingModel.content:
    outgoingModel.content=fitContentModel(opstat.content)
  if not outgoingModel.duration:
    outgoingModel.duration=fitDurationModel(opstat.durations)
#  createPositionModel(outgoingModel, opstat)
  outgoingModel.save()

#def createPositionModel(model, pstat):
#  counts=compilePosition(pstat)
#  fitPositionModel(model, list(counts))
