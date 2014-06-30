# process.py contains helper functions for processing traces to extract
# information to be used in classification of packets by protocol
# These functions are called by the paver tasks in pavement.py

import os
import math
import shutil
from bitstring import BitArray
from scapy.all import sniff, IPv6, IP, UDP, TCP, rdpcap, wrpcap

# Known protocols that we will extract and tag
ports={
  '80': 'http',
  '443': 'SSL',
  '1051': 'obfsproxy',
  '7051': 'Dust'
}

# Generates a stream ID to use for the trace filename, based on sender and receiver IPs and ports and whether it's TCP or UDP
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
    print('Non-IP packet: '+str(packet.summary()))
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
    print('Packet not UDP or TCP: '+str(packet.summary()))
    return None

  id=ut+'_'+src+'_'+str(sport)+'_'+dst+'_'+str(dport)
  return id

# Display packets from a trace
def view(tracefile):
  packets=rdpcap(tracefile)
  for packet in packets:
    id=streamId(packet)
    print(id)

# Split a single trace into multiple traces, one per stream
def splitStreams(tracefile, streamdir):
  packets=rdpcap(tracefile)
  streams={}

  for packet in packets:
    id=streamId(packet)

    if id:
      if id in streams.keys():
        streams[id].append(packet)
      else:
        streams[id]=[packet]

  for id in streams.keys():
    streamfile=streamdir+'/'+id+'.pcap'
    wrpcap(streamfile, streams[id])

# Tag a stream with its protocol based on the ports used
def tagStream(streamfile, tagDir):
  parts=streamfile.split('_')
  print parts
  sport=parts[2]
  dport=parts[4].split('.')[0]
  if sport in ports.keys():
    prot=ports[sport]
  elif dport in ports.keys():
    prot=ports[dport]
  else:
    print('Unknown ports: '+str(sport)+', '+str(dport))
    return

  if '/' in streamfile:
    destfile=streamfile.split('/')[-1]
  else:
    destfile=streamfile
  if not os.path.exists(tagDir):
    os.mkdir(tagDir)
  if not os.path.exists(tagDir+'/'+prot):
    os.mkdir(tagDir+'/'+prot)
  shutil.copyfile(streamfile, tagDir+'/'+prot+'/'+destfile)

# Extract the contents of the packets in a stream and export as a single string
def extractStrings(streamfile, stringfile):
  print('extractStrings '+str(streamfile)+' '+str(stringfile))
  packets=rdpcap(streamfile)
  buff=b''

  for packet in packets:
    if 'Raw' in packet:
      buff=buff+bytes(packet['Raw'])

  f=open(stringfile, 'wb')
  f.write(buff)
  f.close()

# Extract the contents of the first packet in a stream and export as a single string
def extractFirstStrings(streamfile, stringfile):
  print('extractFirstStrings '+str(streamfile)+' '+str(stringfile))
  packets=rdpcap(streamfile)

  for packet in packets:
    if 'Raw' in packet: # First packet with contents
      buff=bytes(packet['Raw'])
      f=open(stringfile, 'wb')
      f.write(buff)
      f.close()
      break

# Extract the substrings in the contents of the packets in a stream, using a sliding window of a fixed size
def extractSubstrings(stringfile, substringfile, size):
  print('extractStrings '+str(stringfile)+' '+str(substringfile))
  f=open(stringfile, 'rb')
  s=f.read()
  f.close()

  f=open(substringfile, 'wb')

  counts={}

  for x in range(len(s)):
    sub=s[x:x+size]
    if len(sub)!=size:
      continue
    bits=BitArray(bytes=sub)
    i=bits.uint
    if i in counts:
      counts[i]=counts[i]+1
    else:
      counts[i]=1

  for key in counts.keys():
    f.write(str(key)+','+str(counts[key])+"\n")
  f.close()

# Extract the first order entropy in the contents of the packets in a stream
def extractEntropy(stringfile, entropyfile):
  print('extractEntropy '+str(stringfile)+' '+str(entropyfile))
  f=open(stringfile, 'rb')
  s=f.read()
  f.close()

  f=open(entropyfile, 'wb')

  total=len(s)
  counts=[0]*256

  for c in s:
    x=ord(c)
    counts[x]=counts[x]+1

  print('counts: '+str(counts))

  u=0
  for count in counts:
    if total==0:
      p=0
    else:
      p=float(count)/float(total)
    if p==0:
      entropy=0
    else:
      entropy=-p*math.log(p, 2)
      print('entropy: '+str(entropy))
    u=u+entropy

  f.write(str(u)+"\n")
  f.close()

# Extract the substrings in the contents of the first 100 packets in a stream, using multiple sliding windows of different sizes
def extractWords(streamfile, words):
  from gensim.corpora.dictionary import Dictionary
  from gensim.corpora import MmCorpus
  print('extractWords '+str(streamfile))
  packets=rdpcap(streamfile)
  buff=b''

  maxSize=4

  # Limit to the first 100 packets
  for x in range(100):
    if x<len(packets):
      if 'Raw' in packets[x]:
        buff=buff+bytes(packets[x]['Raw'])

  for size in range(1, maxSize):
    for x in range(len(buff)):
      sub=buff[x:x+size]
      if len(sub)==size:
        words.append(sub)

  return words

# Convert the extracted words into a format using by the detector
def saveWords(words, wordfile):
  from gensim.corpora.dictionary import Dictionary
  from gensim.corpora import MmCorpus
  dict=Dictionary(words)
  dict.save(wordfile)

# Generate a corpus from the contents of the packets of a stream and a dictionary of words
def extractCorpus(streamfile, dict, corpus):
  from gensim.corpora.dictionary import Dictionary
  from gensim.corpora import MmCorpus
  print('extractCorpus '+str(streamfile))
  packets=rdpcap(streamfile)
  buff=b''

  maxSize=4

  words=[]

  # Limit to the first 100 packets
  for x in range(100):
    if x<len(packets):
      if 'Raw' in packets[x]:
        buff=buff+bytes(packets[x]['Raw'])

  for size in range(1, maxSize):
    for x in range(len(buff)):
      sub=buff[x:x+size]
      if len(sub)==size:
        words.append(sub)

  corpus.append(dict.doc2bow(words))

  return corpus

# Save the corpus in a format usable by the detector
def saveCorpus(corpus, corpusfile):
  from gensim.corpora.dictionary import Dictionary
  from gensim.corpora import MmCorpus
  MmCorpus.serialize(corpusfile, corpus)

# Extract the lengths of the packets in a stream and export to a file containing a list of lengths
def extractLengths(streamfile, lengthfile):
  packets=rdpcap(streamfile)
  lengths=[]

  for packet in packets:
    if 'IP' in packet:
      try:
        l=packet['IP'].fields['len']
      except:
        print('IP packet has no length')
        continue
    elif 'IPv6' in packet:
      try:
        l=packet['IPv6'].fields['len']
      except:
        print('IPv6 packet has no length')
        continue
    else:
      print('Non-IP packet: '+str(packet))
      continue
    lengths.append(l)

  maxlen=max(lengths)
  lengthCount=[0]*(maxlen+1)
  for l in lengths:
    lengthCount[l]=lengthCount[l]+1

  f=open(lengthfile, 'wb')
  for count in lengthCount:
    f.write(str(count)+"\n")
  f.close()

# Extract the timings of the packets in a stream, relative to the first packet, and expot to a file that contains a list of times
def extractTimings(streamfile, timingsfile):
  packets=rdpcap(streamfile)
  s=''
  last=0

  for packet in packets:
    if last==0:
      time=0
    else:
      time=packet.time-last
    last=packet.time

    s=s+str(time)+"\n"

  f=open(timingsfile, 'wb')
  f.write(s)
  f.close()

if __name__=='__main__':
  splitStreams('traces/test/capture.pcap', 'traces/streams')
#  view('traces/test/capture.pcap')
