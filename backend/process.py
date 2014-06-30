import os
import sys

from processUtil import *

filekey=sys.argv[1]

print("Processing %s" % (filekey))

if not os.path.exists('analysis'):
  os.mkdir('analysis')

extractLengths('downloads/'+filekey, 'analysis/'+filekey+'.length')
extractStrings('downloads/'+filekey, 'analysis/'+filekey+'.string')
extractEntropy('analysis/'+filekey+'.string', 'analysis/'+filekey+'.entropy')
extractFirstStrings('downloads/'+filekey, 'analysis/'+filekey+'.string-first')
extractEntropy('analysis/'+filekey+'.string-first', 'analysis/'+filekey+'.entropy-first')
