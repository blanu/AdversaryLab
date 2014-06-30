require 'msgpack'
require 'msgpack/rpc'
require 'net/http/server'
require 'pp'

Net::HTTP::Server.run(:port => 8085) do |request,stream|
  pp request

  filekey=request[:uri][:path].to_s.delete "/"

  pp filekey

  system("./downloadAndProcess.sh %s" % filekey)

  [200, {'Content-Type' => 'text/json'}, [""]]
end
