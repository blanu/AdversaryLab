lastid=0;

function jsonrpc(url, methodName, params)
{
  var id=lastid;
  lastid=lastid+1;
  
  var data=JSON.stringify({'method': methodName, 'params': params, 'id': id});
  $.post(url, data);  
}

function wrap(callback)
{
  if(callback!=null)
  {
    return function(data) {callback(data.result);};
  }
  else
  {
    return function(data) {};
  }
}

function jsonrpcCallback(url, methodName, params, callback)
{
  var id=lastid;
  lastid=lastid+1;

  var data=JSON.stringify({'method': methodName, 'params': params, 'id': id});
  $.post(url, data, wrap(callback));
}

protocol={
  add: function(name)
  {
    jsonrpc('/api/protocol', 'add', [name]);
  },
  list: function(callback)
  {
    jsonrpcCallback('/api/protocol', 'list', [], callback);
  }
};

dataset={
  add: function(name)
  {
    jsonrpc('/api/dataset', 'add', [name]);
  },
  list: function(callback)
  {
    jsonrpcCallback('/api/dataset', 'list', [], callback);
  }
};

pcap={
  setProtocol: function(filekey, name)
  {
    jsonrpc('/api/pcap', 'setProtocol', [filekey, name]);
  },
  setDataset: function(filekey, name)
  {
    jsonrpc('/api/pcap', 'setDataset', [filekey, name]);
  },
  upload: function()
  {
    jsonrpc('/api/pcap', 'uploadCode', []);
  }
};
