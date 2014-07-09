lastid=0;

function jsonrpc(url, methodName, params)
{
  var id=lastid;
  lastid=lastid+1;
  
  var data=JSON.stringify({'method': methodName, 'params': params, 'id': id});
  $.post(url, data);  
}

protocol={
  add: function(name)
  {
    jsonrpc('/api/protocol', 'add', [name]);
  } 
};

dataset={
  add: function(name)
  {
    jsonrpc('/api/dataset', 'add', [name]);
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
