import os
import sys
import json

from processUtil import *

filekey=sys.argv[1]

print("Compiling %s" % (filekey))

if not os.path.exists('compiled'):
  os.mkdir('compiled')

def loadLengths(filekey):
  f=open('analysis/'+filekey+'.length')
  lines=f.readlines()
  lengths=map(int, lines)
  return lengths

def loadEntropy(filename):
  f=open(filename)
  data=f.read().strip()
  f.close()
  return float(data)

def writeCompiled(filekey, compiled):
  f=open('compiled/'+filekey+'.json', 'w')
  f.write(json.dumps(compiled))
  f.close()

lengths=loadLengths(filekey)
entropy=loadEntropy('analysis/'+filekey+'.entropy')
firstEntropy=loadEntropy('analysis/'+filekey+'.entropy-first')
compiled={'filekey': filekey, 'lengths': lengths, 'entropy': entropy, 'entropy-first': firstEntropy}
writeCompiled(filekey, compiled)
