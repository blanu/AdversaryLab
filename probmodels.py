from md5 import md5
import math
import pickle
import pystan
import numpy

import logging

from google.appengine.ext import db

from models import *

def mean(l):
  return float(numpy.mean(l))

def stan_cache(model_name, **kwargs):
  f=open(model_name, 'rb')
  model_code=f.read()
  f.close()
  code_hash = md5(model_code.encode('ascii')).hexdigest()
  cache_fn = 'cached-{}-{}.pkl'.format(model_name, code_hash)
  try:
    sm = pickle.load(open(cache_fn, 'rb'))
  except:
    sm = pystan.StanModel(file=model_name)
    with open(cache_fn, 'wb') as f:
      pickle.dump(sm, f)
  else:
    logging.info("Using cached StanModel")
  return sm.sampling(**kwargs)

class Normal(db.Model):
  mean=db.FloatProperty(required=True)
  sd=db.FloatProperty(required=True)

class Multinomial(db.Model):
  distribution=db.ListProperty(float)

class Exponential(db.Model):
  parameter=db.FloatProperty(required=True)

class Poisson(db.Model):
  parameter=db.FloatProperty(required=True)

class LengthModel(db.Model):
  distribution=db.ReferenceProperty(Normal, required=True)

class DurationModel(db.Model):
  distribution=db.ReferenceProperty(Exponential, required=True)

class EntropyModel(db.Model):
  distribution=db.ReferenceProperty(Normal, required=True)

class FlowModel(db.Model):
  distribution=db.ReferenceProperty(Poisson, required=True)

class ContentModel(db.Model):
  distribution=db.ReferenceProperty(Multinomial, required=True)

class ProtocolModel(db.Model):
  protocol=db.ReferenceProperty(Protocol, required=True)
  dataset=db.ReferenceProperty(Dataset, required=True)
  outgoing=db.BooleanProperty(required=True)
  length=db.ReferenceProperty(LengthModel, required=False)
  entropy=db.ReferenceProperty(EntropyModel, required=False)
  flow=db.ReferenceProperty(FlowModel, required=False)
  content=db.ReferenceProperty(ContentModel, required=False)
  duration=db.ReferenceProperty(DurationModel, required=False)

class AdversaryProtocolModel(db.Model):
  adversary=db.ReferenceProperty(AdversaryModel, required=True)
  label=db.BooleanProperty(required=True)
  outgoing=db.BooleanProperty(required=True)
  length=db.ReferenceProperty(LengthModel, required=False)
  entropy=db.ReferenceProperty(EntropyModel, required=False)
  flow=db.ReferenceProperty(FlowModel, required=False)
  content=db.ReferenceProperty(ContentModel, required=False)
  duration=db.ReferenceProperty(DurationModel, required=False)

class PositionModel(db.Model):
  model=db.ReferenceProperty(ProtocolModel, required=True)
  position=db.IntegerProperty(required=True)
  previous=db.IntegerProperty(required=True)
  distribution=db.ReferenceProperty(Multinomial, required=True)

class Fit(db.Model):
  conn=db.ReferenceProperty(Connection, required=True)
  model=db.ReferenceProperty(AdversaryProtocolModel, required=True)
  length=db.FloatProperty(required=True)
  entropy=db.FloatProperty(required=True)
  flow=db.FloatProperty(required=True)
  content=db.FloatProperty(required=True)
  duration=db.FloatProperty(required=True)

def fitLengthModel(lengths):
  if not lengths:
    return None

  lengths=filter(lambda x: x<=1440, lengths)

  if len(lengths)<3:
    return None

  logging.info("fitting length with %d samples" % (len(lengths)))

  data={'samples': lengths, 'N': len(lengths)}
  fit=stan_cache('length.stan', data=data, iter=1000, chains=4)
  logging.info(fit)
  samples=fit.extract(permuted=True)
  logging.info(samples)
  theta1=mean(samples['theta'])
  sigma1=mean(samples['sigma'])
  logging.info((theta1, sigma1))
  logging.info('Length results:')
  logging.info(list((theta1, sigma1)))
  normal=Normal(mean=theta1, sd=sigma1)
  normal.save()
  logging.info(normal)
  model=LengthModel(distribution=normal)
  model.save()
  logging.info(model)
  return model

def fitDurationModel(lengths):
  lengths=filter(checkEntropy, lengths)
  if not lengths or len(lengths)<3:
    logging.error("Not enough samples for duration model")
    return None

  data={'samples': lengths, 'N': len(lengths)}
  fit=stan_cache('duration.stan', data=data, iter=1000, chains=4)
  logging.info(fit)
  samples=fit.extract(permuted=True)
  logging.info(samples)
  l=mean(samples['lambda'])
  logging.info(l)
  exp=Exponential(parameter=l)
  exp.save()
  model=DurationModel(distribution=exp)
  model.save()
  return model

def fitEntropyModel(samples):
  logging.info("Not enough samples for entropy model")
  if not samples or len(samples)<3:
    return None

  samples=filter(checkEntropy, samples)

  logging.info('Fitting entropy:')
  logging.info(samples)
  data={'samples': samples, 'N': len(samples)}
  fit=stan_cache('entropy.stan', data=data, iter=1000, chains=4)
  logging.info(fit)
  samples=fit.extract(permuted=True)
  logging.info(samples)
  theta1=mean(samples['theta'])
  sigma1=mean(samples['sigma'])
  logging.info((theta1, sigma1))
  logging.info(list((theta1, sigma1)))
  normal=Normal(mean=theta1, sd=sigma1)
  normal.save()
  model=EntropyModel(distribution=normal)
  model.save()
  return model

def checkEntropy(sample):
  return sample>0

def fitFlowModel(samples):
  if not samples or len(samples)<3:
    return None

  data={'samples': samples, 'N': len(samples)}
  fit=stan_cache('flow.stan', data=data, iter=1000, chains=4)
  logging.info(fit)
  samples=fit.extract(permuted=True)
  logging.info(samples)
  l=mean(samples['lambda'])
  logging.info(l)
  pois=Poisson(parameter=l)
  pois.save()
  model=FlowModel(distribution=pois)
  model.save()
  return model

def fitContentModel(counts):
  if not counts or len(counts)!=256:
    return None

  logging.info('Fitting content model:')
  logging.info(counts)
  data={'counts': counts}
  fit=stan_cache('content.stan', data=data, iter=1000, chains=2)
  logging.info('Loaded model')
  samples=fit.extract(permuted=True)
  thetas=samples['theta']
  theta=map(float, list(thetas[0])) # FIXME - This is a bad way to generate a summary statistic for theta
  logging.info(theta)
  multi=Multinomial(distribution=theta)
  multi.save()
  model=ContentModel(distribution=multi)
  model.save()
  return model

def fitPositionModel(model, counts):
  if not counts or len(counts)<256:
    return None

  data={'L': 1440, 'B': 256, 'counts': counts}
  fit=stan_cache('position.stan', data=data, iter=1000, chains=4)
  logging.info(fit)
  samples=fit.extract(permuted=True)
  logging.info(samples)
  thetas=samples['theta']
  logging.info(theta)
  for l in range(1440):
    for b in range(256):
      theta=thetas[l][b]
      model=PositionModel(model=model, position=l, previous=b, distribution=theta)
      model.save()
