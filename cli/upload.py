import sys
import requests
from jsonrpc.proxy import ServiceProxy

filename=sys.argv[1]

baseurl='http://www.adversarylab.org/'

rpc=ServiceProxy(baseurl+'/api/pcap')
code=rpc.uploadCode()

requests.post(code, files={'pcapFile': open(filename,'rb')})
