from md5 import md5
import math
import pickle
import pystan

import logging

#from models import *

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
    print("Using cached StanModel")
  return sm.sampling(**kwargs)

def fitLengthModel(lengths):
  data={'packetLength': lengths, 'samples': len(lengths)}
  fit=stan_cache('length.stan', data=data, iter=1000, chains=4)
  logging.info(fit)
  samples=fit.extract(permuted=True)
  print(samples)
  theta1=samples['theta1']
  sigma1=samples['sigma1']
  logging.info((theta1, sigma1))
  print(list((theta1, sigma1)))
