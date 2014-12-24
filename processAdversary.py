from random import choice
import numpy
from numpy.random import normal, poisson, exponential, multinomial
from google.appengine.datastore.datastore_query import Cursor

from models import *
from probmodels import *

class ProtocolStatInfo:
  def __init__(self):
    self.sizes=[0]*1500
    self.content=[0]*256
    self.entropies=[]
    self.flow=[]

def processAdversary(adversary, pcaps):
  results=[]
  for pcap in pcaps:
    results=results+adversary.processPcap(pcap)
  return summarize(results)

def summarize(results):
  total=len(results)
  counts=[[0,0],[0,0]]
  for (guess,correct) in results:
    counts[int(guess)][int(correct)]=counts[int(guess)][int(correct)]+1
  cl=[[count/total for count in l] for l in counts]
  return cl

def combineProtocol(pcapFile, durations, ipstat, opstat):
  pageSize=500
  offset=0
  more=True
  while more:
    conns=Connection().all().ancestor(pcapFile).fetch(pageSize, offset=offset)
    logging.info("Found %d conns at offset %d %s" % (Connection().all().filter("pcap =", pcapFile).count(limit=pageSize, offset=offset), offset, str(pcapFile)))
    offset=offset+pageSize

    if not conns or len(conns)<pageSize:
      more=False

    for pcap in conns:
      for x in range(1500):
        ipstat.sizes[x]=ipstat.sizes[x]+pcap.incomingStats.lengths[x]
        opstat.sizes[x]=opstat.sizes[x]+pcap.outgoingStats.lengths[x]
      for x in range(256):
        ipstat.content[x]=ipstat.content[x]+pcap.incomingStats.content[x]
        opstat.content[x]=opstat.content[x]+pcap.outgoingStats.content[x]
      ipstat.entropies.append(pcap.incomingStats.entropy)
      opstat.entropies.append(pcap.outgoingStats.entropy)
      for count in pcap.incomingStats.flow:
        ipstat.flow.append(count)
      for count in pcap.outgoingStats.flow:
        opstat.flow.append(count)
      if pcap.duration!=0:
        durations.append(pcap.duration)

  return durations, ipstat, opstat

def trainAdversaryByName(name):
  adversary=AdversaryModel.all().filter("name =", name).get()
  if adversary:
    for label in [True, False]:
      durations=[]
      ipstat=ProtocolStatInfo()
      opstat=ProtocolStatInfo()
      data=LabeledData.all().filter("adversary =", adversary).filter("training =", True).filter("label =", label).run()
      if data:
        for datum in data:
          # try:
          durations, ipstat, opstat=combineProtocol(datum.pcap, durations, ipstat, opstat)
          trainAdversary(adversary, label, durations, ipstat, opstat)
          logging.info('Success')
          # except Exception as e:
          #   logging.error('Failure, could not read connections')
          #   logging.error(e)
          #   logging.error("...")
      else:
        logging.info('Failure, no data')
  else:
    logging.info('Failure, no adversary')

def trainAdversary(adversary, label, durations, ipstat, opstat):
  logging.info("trainAdverary label=%s" % (str(label)))
  for direction, stat in [(True,opstat), (False,ipstat)]:
    logging.info("trainAdverary label=%s direction=%s" % (str(label), str(direction)))
    count=AdversaryProtocolModel.all().ancestor(adversary).filter('label =', label).filter('outgoing =', direction).count()
    if count==0:
      model=AdversaryProtocolModel(parent=adversary, adversary=adversary, label=label, outgoing=direction)
    elif count==1:
      model=AdversaryProtocolModel.all().ancestor(adversary).filter('label =', label).filter('outgoing =', direction).get()
    else:
      logging.error("Warning, multiple models found %d" % (count))
      model=AdversaryProtocolModel.all().ancestor(adversary).filter('label =', label).filter('outgoing =', direction).get()
    if not model.length or not model.length.distribution:
      model.length=fitLengthModel(stat.sizes)
    if not model.entropy or not model.entropy.distribution:
      model.entropy=fitEntropyModel(stat.entropies)
    if not model.flow:
      model.flow=fitFlowModel(stat.flow)
    if not model.content:
      model.content=fitContentModel(stat.content)
    if not model.duration:
      model.duration=fitDurationModel(durations)
    logging.info("Saving label=%s direction=%s" % (str(label), str(direction)))
    model.save()

def checkFitLengthModel(model, stats):
  sampleSize=1000
  bounds=[1,1440]
  countsA=generateNormalCounts(model, sampleSize, bounds)
  countsB=generateBootstrapCounts(stats, sampleSize, bounds)
  return compareCounts(countsA, countsB)

def checkFitContentModel(model, stats):
  sampleSize=1000
  bounds=[0,255]
  countsA=generateMultinomialCounts(model, sampleSize, bounds)
  countsB=generateBootstrapCounts(stats, sampleSize, bounds)
  return compareCounts(countsA, countsB)

def checkFitEntropyModel(model, stats):
  sampleSize=1000
  samplesA=generateNormalSamples(model, sampleSize)
  samplesB=generateBootstrapSamples(stats, sampleSize)
  return compareSamples(samplesA, samplesB)

def checkFitFlowModel(model, stats):
  sampleSize=1000
  statlist=[]
  for stat in stats:
    statlist.append(stat)
  samples=generatePoissonSamples(model, len(statlist), sampleSize)
  return compareSamples(samples, statlist)

def checkFitDurationModel(model, stats):
  sampleSize=1000
  samplesA=generateExponentialSamples(model, sampleSize)
  samplesB=generateBootstrapSamples(stats, sampleSize)
  return compareSamples(samplesA, samplesB)

def generateMultinomialCounts(model, sampleSize, bounds):
  dist=model.distribution.distribution
  return list(multinomial(sampleSize, list(dist)))

def generateNormalCounts(model, sampleSize, bounds):
  mean=model.distribution.mean
  sd=model.distribution.sd
  size=bounds[1]-bounds[0]
  counts=[0]*size
  samples=normal(mean, sd, sampleSize)
  for sample in samples:
    if sample>bounds[0] and sample<bounds[1]:
      index=int(sample-bounds[0])
      counts[index]=counts[index]+1
  return counts

def generateNormalSamples(model, sampleSize):
  mean=model.distribution.mean
  sd=model.distribution.sd
  return normal(mean, sd, sampleSize)

def generatePoissonSamples(model, numSlots, sampleSize):
  l=model.distribution.parameter
  samples=[]
  for slot in range(numSlots):
    samples.append(poisson(l, sampleSize))
  return samples

def generateExponentialSamples(model, sampleSize):
  beta=model.distribution.parameter
  return exponential(beta, sampleSize)

def generateBootstrapCounts(stats, sampleSize, bounds):
  size=(bounds[1]-bounds[0])+1
  counts=[0]*size
  samples=[]
  for x in range(sampleSize):
    samples.append(choice(stats))
  for sample in samples:
    if sample>bounds[0] and sample<bounds[1]:
      index=sample-bounds[0]
      counts[index]=counts[index]+1
  return counts

def generateBootstrapSamples(stats, sampleSize):
  samples=[]
  for x in range(sampleSize):
    samples.append(choice(stats))
  return samples

def compareCounts(countsA, countsB):
  e=0
  size=len(countsA)
  for x in range(size):
    a=countsA[x]
    b=countsB[x]
    e=e+rmse(a,b)
  return e

def compareSampleSets(setA, setB):
  e=0
  size=len(setA)
  for x in range(size):
    samplesA=setA[x]
    samplesB=setB[x]
    for y in range(len(samplesA)):
      a=samplesA[y]
      b=samplesB[y]
      e=e+rmse(a,b)
  return e

def compareSamples(samplesA, samplesB):
  e=0
  size=len(samplesA)
  for x in range(size):
    a=samplesA[x]
    b=samplesB[x]
    e=e+rmse(a,b)
  return e

def rmse(predictions, targets):
  return numpy.sqrt(numpy.mean((predictions - targets) ** 2))

class ConnStats:
  def __init__(self):
    length=[] # by packet
    entropy=[] # by packet
    flow=[] # whole connection, by millisecond
    content=[] # whole connection, counts by byte
    duration=0 # whole connection

def checkModels(models):
  for x in range(len(models)):
    model=models[x]
    if not checkModel(model):
      logging.error("Bad model %d %s" % (x, str(model)))
      return False

def checkModel(model):
  if not model.duration or not model.duration.distribution:
    return False
  elif not model.flow or not model.flow.distribution:
    False
  elif not model.length or not model.length.distribution:
    False
  elif not model.entropy or not model.entropy.distribution:
    False
  elif not model.content or not model.content.distribution:
    False
  else:
    return True

def testAdversary(adversary):
  logging.info('testAdversary')
  pfits=[]
  nfits=[]
  pimodel=AdversaryProtocolModel.all().ancestor(adversary).filter('label =', True).filter('outgoing =', False).get()
  nimodel=AdversaryProtocolModel.all().ancestor(adversary).filter('label =', False).filter('outgoing =', False).get()
  pomodel=AdversaryProtocolModel.all().ancestor(adversary).filter('label =', True).filter('outgoing =', True).get()
  nomodel=AdversaryProtocolModel.all().ancestor(adversary).filter('label =', False).filter('outgoing =', True).get()
  if not checkModels([pimodel, nimodel, pomodel, nomodel]):
    logging.error('Model check failed')
  for label, fits in [(True, pfits), (False, nfits)]:
    data=LabeledData.all().filter('adversary =', adversary).filter('training =', False).filter('label =', label).run()
    if data:
      pcaps=[]
      for datum in data:
        pcaps.append(datum.pcap)
      logging.info('Found %d pcaps' % (len(pcaps)))
      if len(pcaps)>0:
        if not (pimodel and pomodel and nimodel and nomodel):
          logging.error('Missing models, cannot proceed')
          return
        for pcap in pcaps:
          pageSize=500
          offset=0
          more=True
          while more:
            conns=Connection.all().ancestor(pcap).fetch(pageSize, offset)
            offset=offset+pageSize
            if not conns or len(conns)<pageSize:
              more=False
            for conn in conns:
              connfits=[]
              for models in [[pimodel,pomodel],[nimodel,nomodel]]:
                for portIndex, stats in [(0,conn.incomingStats),(1,conn.outgoingStats)]:
                  model=models[portIndex]
                  length=checkFitLengthModel(model.length, stats.lengths)
                  if model.entropy and model.entropy.distribution:
                    entropy=checkFitEntropyModel(model.entropy, [stats.entropy])
                  else:
                    entropy=0
                  if model.flow and model.flow.distribution:
                    flow=checkFitFlowModel(model.flow, stats.flow)
                  else:
                    flow=0
                  content=checkFitContentModel(model.content, stats.content)
                  if conn.duration!=0 and model.duration and model.duration.distribution:
                    duration=checkFitDurationModel(model.duration, [conn.duration])
                  else:
                    duration=0
                  fit=Fit(parent=model, conn=conn, model=model, length=float(length), entropy=float(entropy), flow=float(flow), content=float(content), duration=float(duration))
                  fit.save()
                  connfits.append(fit)
              fits.append(connfits)
  pfits=combineFits(pfits)
  nfits=combineFits(nfits)
  logging.info('pfits:')
  logging.info(pfits)
  logging.info('nfits:')
  logging.info(nfits)
  pscore=score(pfits, True)
  nscore=score(nfits, False)
  logging.info("Scores: %f %f" % (pscore, nscore))
  return pscore, nscore

class OverallFit:
  def __init__(self):
    length=0
    flow=0
    content=0
    entropy=0
    duration=0

def combineFits(fits):
  results=[]

  logging.info('Fits:')
  logging.info(fits)

  for connfits in fits:
    pifit=connfits[0]
    pofit=connfits[1]
    nifit=connfits[2]
    nofit=connfits[3]

    ifit=OverallFit()
    ifit.length=cmp(pifit.length, nifit.length)
    ifit.flow=cmp(pifit.flow, nifit.flow)
    ifit.content=cmp(pifit.content, nifit.content)
    ifit.duration=cmp(pifit.duration, nifit.duration)
    ifit.entropy=cmp(pifit.entropy, nifit.entropy)

    ofit=OverallFit()
    ofit.length=cmp(pofit.length, nofit.length)
    ofit.flow=cmp(pofit.flow, nofit.flow)
    ofit.content=cmp(pofit.content, nofit.content)
    ofit.duration=cmp(pofit.duration, nofit.duration)
    ofit.entropy=cmp(pofit.entropy, nofit.entropy)

    result=ifit.length+ofit.length+ifit.flow+ofit.flow+ifit.content+ofit.content+ifit.duration+ofit.duration+ifit.entropy+ofit.entropy
    results.append(result)
  return results

def score(fits, label):
  size=len(fits)
  if size==0:
    logging.error('Error, no fit data to score')
    return 0
  else:
    count=0
    for fit in fits:
      if (label and fit>0) or (not label and fit<0):
        count=count+1
    return float(count)/float(size)
