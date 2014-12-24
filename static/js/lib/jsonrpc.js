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

user={
  isLoggedIn: function(callback)
  {
    jsonrpcCallback('/api/user', 'isLoggedIn', [], callback);
  },
  isAdmin: function(callback)
  {
    jsonrpcCallback('/api/user', 'isAdmin', [], callback);
  },
  isMember: function(callback)
  {
    jsonrpcCallback('/api/user', 'isMember', [], callback);
  },
  login: function(callback)
  {
    jsonrpcCallback('/api/user', 'login', [], callback);
  },
  logout: function(callback)
  {
    jsonrpcCallback('/api/user', 'logout', [], callback);
  },
  apply: function(username, application)
  {
    jsonrpc('/api/user', 'apply', [username, application]);
  },
  hasApplied: function(callback)
  {
    jsonrpcCallback('/api/user', 'hasApplied', [], callback);
  }
};

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

adversary={
  add: function(name)
  {
    jsonrpc('/api/adversary', 'add', [name]);
  },
  list: function(callback)
  {
    jsonrpcCallback('/api/adversary', 'list', [], callback);
  },
  pcaps: function(name, callback)
  {
    jsonrpcCallback('/api/adversary', 'pcaps', [name], callback);
  },
  sort: function(name, filename, training, label, callback)
  {
    jsonrpcCallback('/api/adversary', 'sort', [name, filename, training, label], callback);
  },
  unsort: function(name, filename, callback)
  {
    jsonrpcCallback('/api/adversary', 'unsort', [name, filename], callback);
  },
  train: function(name)
  {
    jsonrpc('/api/adversary', 'train', [name]);
  },
  test: function(name)
  {
    jsonrpc('/api/adversary', 'test', [name]);
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
  upload: function(callback)
  {
    jsonrpcCallback('/api/pcap', 'uploadCode', [], callback);
  },
  list: function(callback)
  {
    jsonrpcCallback('/api/pcap', 'list', [], callback);
  }
};

reports={
  getForPcap: function(filekey, callback)
  {
    jsonrpcCallback('/api/report', 'getForPcap', [filekey], callback);
  },
  getForDatasetAndProtocol: function(dataset, protocol, callback)
  {
    jsonrpcCallback('/api/report', 'getForDatasetAndProtocol', [dataset, protocol], callback);
  },
  getForProtocol: function(filekey, callback)
  {
    jsonrpcCallback('/api/report', 'getForProtocol', [filekey], callback);
  },
  generateModel: function(dataset, protocol)
  {
    jsonrpc('/api/report', 'generateModel', [dataset, protocol]);
  },
  rerun: function()
  {
    jsonrpc('/api/report', 'rerun', []);
  },
  rerunPcap: function(filekey)
  {
    jsonrpc('/api/report', 'rerunPcap', [filekey]);
  }
};
